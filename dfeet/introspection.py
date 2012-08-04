# -*- coding: utf-8 -*-

from gi.repository import GObject, Gdk, GdkPixbuf, Gtk, Gio, Pango, GLib
import dbus_utils
from _ui.executemethoddialog import ExecuteMethodDialog
import time

from _ui.uiloader import UILoader

from introspection_helper import DBusNode, DBusInterface, DBusProperty, DBusSignal, DBusMethod


class AddressInfo():
    """
    class to handle information about a name (eg "org.freedesktop.NetworkManager")
    on a given address (eg Gio.BusType.SYSTEM or unix:path=/var/run/dbus/system_bus_socket)
    """
    def __init__(self, address, name, connection_is_bus=True):
        self.address = address # can be Gio.BusType.SYSTEM or Gio.BusType.SYSTEM or an other address
        self.name = name
        self.connection_is_bus = connection_is_bus # is it a bus or a p2p connection?
        self.introspect_time = -1 # time needed to introspect the given bus name (in seconds)

        #setup UI
        ui = UILoader(UILoader.UI_INTROSPECTION)
        self.introspect_box = ui.get_root_widget()
        self.tree_model = ui.get_widget('treestore')
        self.treeview = ui.get_widget('treeview')
        button_reload = ui.get_widget('button_reload')
        self.label_name = ui.get_widget('label_name')
        self.label_unique_name = ui.get_widget('label_unique_name')
        self.label_address = ui.get_widget('label_address')
        cr_name = Gtk.CellRendererText()
        col_name = Gtk.TreeViewColumn()
        col_name.pack_start(cr_name, True)
        col_name.add_attribute(cr_name, 'markup', 0)
        self.treeview.append_column(col_name)

        #connect signals
        button_reload.connect("clicked", self.__on_button_reload_clicked, self)
        self.treeview.connect('cursor-changed',
                               self.tree_view_cursor_changed_cb)
        self.treeview.connect('row-activated', 
                               self.tree_view_row_activated_cb)

        if self.connection_is_bus:
            #we expect a bus connection
            if self.address == Gio.BusType.SYSTEM or self.address == Gio.BusType.SESSION:
                self.connection = Gio.bus_get_sync(self.address, None)
                self.label_address.set_text(Gio.dbus_address_get_for_bus_sync(self.address, None))
            elif Gio.dbus_is_supported_address(self.address) == True:
                self.connection = Gio.DBusConnection.new_for_address_sync(self.address,
                                                                          Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
                                                                          None, None)
                self.label_address.set_text(self.address)
            else:
                self.connection = None
                raise Exception("Invalid bus address '%'" % (self.address))
        else:
            #we have a peer-to-peer connection
            if Gio.dbus_is_supported_address(self.address) == True:
                self.connection = Gio.DBusConnection.new_for_address_sync(self.address,
                                                                          Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT,
                                                                          None, None)
                self.label_address.set_text(self.address)
            else:
                self.connection = None
                raise Exception("Invalid p2p address '%'" % (self.address))
            
        #start processing data
        self.introspect()
        self.treeview.expand_all() #FIXME: only good for testing!
    
    def tree_view_cursor_changed_cb(self, treeview):
        """ do something when a row is selected """
        selection = self.treeview.get_selection()
        if selection:
            model, iter = selection.get_selected()
            if not iter:
                return
        
            node_obj = model.get(iter, 1)[0]
            #print "NODE: %s" % (node_obj)

    def tree_view_row_activated_cb(self, treeview, path, view_column):
        model = treeview.get_model() 
        iter = model.get_iter(path)

        obj = model.get_value(iter, 1)

        if isinstance(obj, DBusMethod):
            #execute the selected method
            dialog = ExecuteMethodDialog(self.connection, self.connection_is_bus, self.name, obj)
            dialog.run()
        elif isinstance(obj, DBusProperty):
            #update the selected property (TODO: do this async)
            proxy = Gio.DBusProxy.new_sync(self.connection,
                                           Gio.DBusProxyFlags.NONE, 
                                           None, 
                                           self.name,
                                           obj.object_path,
                                           "org.freedesktop.DBus.Properties", None)
            args = GLib.Variant('(ss)', (obj.iface_info.name, obj.property_info.name))
            result = proxy.call_sync("Get", args, 0, -1, None)
            #update the object value so markup string is calculated correct
            obj.value = result[0]
            #set new markup string
            model[iter][0] = obj.markup_str
        else:
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, False)


    def introspect(self):
        """ introspect the given bus name and update the tree model """
        #cleanup current tree model
        self.tree_model.clear()
        #start introspection and measure introspection time
        introspect_start = time.time()
        self.__dbus_node_introspect(self.name, "/")
        self.introspect_time = time.time() - introspect_start
        #update name, unique name, ...
        self.label_name.set_text(self.name)
        try:
            self.label_unique_name.set_text(self.connection.get_unique_name())
        except:
            pass


    def __on_button_reload_clicked(self, widget, address_info):
        """ reload the introspection data """
        address_info.introspect()
        print "needed %.3f s to introspect name '%s'" % (address_info.introspect_time, address_info.name)


    def __dbus_node_introspect(self, name, object_path):
        """ iterate over the given object_path and introspect the path recursive """
        tree_iter = None
        if self.connection_is_bus:
            proxy = Gio.DBusProxy.new_sync(self.connection,
                                           Gio.DBusProxyFlags.NONE, 
                                           None, 
                                           name,
                                           object_path,
                                           'org.freedesktop.DBus.Introspectable', None)
            node_info = Gio.DBusNodeInfo.new_for_xml(proxy.Introspect())
        else:
            res = self.connection.call_sync(None, object_path, 'org.freedesktop.DBus.Introspectable', 'Introspect', None, GLib.VariantType.new("(s)"), Gio.DBusCallFlags.NONE, -1, None)
            node_info = Gio.DBusNodeInfo.new_for_xml(res[0])

        #create a GObject node and add to tree-model
        if len(node_info.interfaces) > 0:
            node_obj = DBusNode(name, object_path, node_info)
            tree_iter = self.tree_model.append(tree_iter, ["%s" % object_path, node_obj])
            #tree_iter = self.tree_model.append(tree_iter, ["Hallo", None])

            #append interfaces to tree model
            if len(node_info.interfaces) > 0:
                name_iter = self.tree_model.append(tree_iter, ["<b>Interfaces</b>", None])
                for iface in node_info.interfaces:
                    iface_obj = DBusInterface(node_obj, iface)
                    iface_iter = self.tree_model.append(name_iter, ["%s" % iface.name, iface_obj])
                    #interface methods
                    if len(iface.methods) > 0:
                        iface_methods_iter = self.tree_model.append(iface_iter, ["<b>Methods</b>", None])
                        for iface_method in iface.methods:
                            method_obj = DBusMethod(iface_obj, iface_method)
                            self.tree_model.append(iface_methods_iter, ["%s" % method_obj.markup_str, method_obj])
                    #interface signals
                    if len(iface.signals) > 0:
                        iface_signals_iter = self.tree_model.append(iface_iter, ["<b>Signals</b>", None])
                        for iface_signal in iface.signals:
                            signal_obj = DBusSignal(iface_obj, iface_signal)
                            self.tree_model.append(iface_signals_iter, ["%s" % signal_obj.markup_str, signal_obj])
                    #interface properties
                    if len(iface.properties) > 0:
                        iface_properties_iter = self.tree_model.append(iface_iter, ["<b>Properties</b>", None])
                        for iface_property in iface.properties:
                            property_obj = DBusProperty(iface_obj, iface_property)
                            self.tree_model.append(iface_properties_iter, ["%s" % property_obj.markup_str, property_obj])
                    #interface annotations #FIXME: add Annotation object!!!
                    if len(iface.annotations) > 0:
                        iface_annotations_iter = self.tree_model.append(iface_iter, ["<b>Annotations</b>", None])
                        for iface_annotation in iface.annotations:
                            self.tree_model.append(iface_annotations_iter, ["%s" % iface_annotation.name, iface_annotation])
                    

        for node in node_info.nodes:
            #node_iter = self.tree_model.append(tree_iter, [node.path, node])
            if object_path == "/":
                object_path = ""
            object_path_new = object_path + "/" + node.path
            self.__dbus_node_introspect(name, object_path_new)



if __name__ == "__main__":
    """ for debugging """
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='introspect a given dbus address and name')
    parser.add_argument('-p', '--p2p', action='store_true', default=False)
    parser.add_argument('addr')
    parser.add_argument('name')
    p = parser.parse_args()

    if p.addr.lower() == 'system':
        addr = Gio.BusType.SYSTEM
    elif p.addr.lower() == 'session':
        addr = Gio.BusType.SESSION
    else:
        addr = p.addr

    
    name = p.name
    ai = AddressInfo(addr, name, not p.p2p)

    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(1024, 768)
    win.add(ai.introspect_box)
    win.show_all()
    try:
        Gtk.main()
    except (KeyboardInterrupt, SystemExit):
        Gtk.main_quit()
