# -*- coding: utf-8 -*-

from gi.repository import GObject, Gtk, Gio
from _ui.uiloader import UILoader
from introspection import AddressInfo


class DBusBusName(GObject.GObject):
    """class to represent a name on the bus"""
    def __init__(self, bus_name_unique):
        super(DBusBusName, self).__init__()
        self.__bus_name_unique = bus_name_unique
        self.__pid = 0
        self.__cmdline = ''

    def __repr__(self):
        return u"%s (pid: %s)" % (self.bus_name_unique, self.pid)

    def __update_cmdline(self):
        if self.pid > 0:
            procpath = '/proc/' + str(self.pid) + '/cmdline'
            with open(procpath, 'r') as f:
                self.__cmdline = " ".join(f.readline().split('\0'))
        else:
            self.__cmdline = ''

    @property
    def bus_name_unique(self):
        return self.__bus_name_unique

    @property
    def pid(self):
        return self.__pid
    
    @pid.setter
    def pid(self, pid_new):
        self.__pid = pid_new
        try:
            self.__update_cmdline()
        except:
            self.__cmdline = ''

    @property
    def cmdline(self):
        return self.__cmdline


class BusWatch(object):
    """watch for a given bus"""
    def __init__(self, address):
        self.address = address
        #setup UI
        ui = UILoader(UILoader.UI_BUSWATCH)
        self.paned_buswatch = ui.get_root_widget()
        self.liststore_model = ui.get_widget('liststore_buswatch')
        self.treemodelfilter_buswatch = ui.get_widget('treemodelfilter_buswatch')
        self.treemodelfilter_buswatch.set_visible_func(self.__treemodelfilter_buswatch_cb)
        self.treemodelsort_buswatch = ui.get_widget("treemodelsort_buswatch")
        self.treemodelsort_buswatch.set_sort_func(2, self.__sort_on_name)
        self.treemodelsort_buswatch.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        self.treeview = ui.get_widget('treeview_buswatch')
        self.entry_filter = ui.get_widget('entry_filter')
        self.grid_bus_name_selected_info = ui.get_widget('grid_bus_name_info')
        self.label_bus_name_selected_name = ui.get_widget('label_bus_name_selected_name')
        self.label_bus_name_selected_pid = ui.get_widget('label_bus_name_selected_pid')
        self.label_bus_name_selected_cmdline = ui.get_widget('label_bus_name_selected_cmdline')
        self.addr_info = None # hold the currently selected AddressInfo object

        self.treeview.connect('cursor-changed',
                               self.__tree_view_cursor_changed_cb)
        self.entry_filter.connect("changed",
                                  self.__entry_filter_changed_cb)


        #setup the conection
        if self.address == Gio.BusType.SYSTEM or self.address == Gio.BusType.SESSION:
            self.connection = Gio.bus_get_sync(self.address, None)
        elif Gio.dbus_is_supported_address(self.address):
            self.connection = Gio.DBusConnection.new_for_address_sync(self.address,
                                                                      Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
                                                                      None, None)

        #setup signals
        self.connection.signal_subscribe(None, "org.freedesktop.DBus", "NameOwnerChanged",
                                         None, None, 0, self.__name_owner_changed_cb, None)

        self.bus_proxy = Gio.DBusProxy.new_sync(self.connection,
                                                Gio.DBusProxyFlags.NONE, 
                                                None, 
                                                'org.freedesktop.DBus',
                                                '/org/freedesktop/DBus',
                                                'org.freedesktop.DBus', None)

        #list all names
        self.bus_proxy.ListNames('()',
                                 result_handler=self.__list_names_handler,
                                 error_handler=self.__list_names_error_handler)


    def __treemodelfilter_buswatch_cb(self, model, iter, user_data):
        #return model.get_value(iter, 1) in data
        bus_name_obj = model.get(iter, 0)[0]
        filter_text = self.entry_filter.get_text()
        return filter_text.lower() in bus_name_obj.bus_name_unique.lower()

    def __entry_filter_changed_cb(self, entry_filter):
        self.treemodelfilter_buswatch.refilter()


    def __tree_view_cursor_changed_cb(self, treeview):
        """do something when a row is selected"""
        selection = self.treeview.get_selection()
        if selection:
            model, iter_ = selection.get_selected()
            if not iter_:
                return
        
            bus_name_obj = model.get(iter_, 0)[0]
            #remove current child
            c2 = self.paned_buswatch.get_child2()
            if c2:
                c2.destroy()
            try:
                del(self.addr_info)
            except:
                pass

            #add Introspection to paned
            self.addr_info = AddressInfo(self.address, bus_name_obj.bus_name_unique, connection_is_bus=True)
            self.paned_buswatch.add2(self.addr_info.introspect_box)
            
            #update info about selected bus name
            self.label_bus_name_selected_name.set_text(bus_name_obj.bus_name_unique)
            self.label_bus_name_selected_pid.set_text("%s" % bus_name_obj.pid)
            self.label_bus_name_selected_cmdline.set_text(bus_name_obj.cmdline)
            self.grid_bus_name_selected_info.set_visible(True)
            

    def __liststore_model_add(self, bus_name_obj):
        """add a DBusBusName object to the liststore model"""
        #update bus info stuff
        self.bus_proxy.GetConnectionUnixProcessID('(s)', bus_name_obj.bus_name_unique, 
                                                  result_handler = self.__get_unix_process_id_cb,
                                                  error_handler =  self.__get_unix_process_id_error_cb,
                                                  user_data=bus_name_obj)
        #add bus to liststore
        return self.liststore_model.append([bus_name_obj, 0, u"%s" % (bus_name_obj.bus_name_unique), bus_name_obj.cmdline])


    def __liststore_model_remove(self, bus_name_obj):
        """remove a DBusBusName object to the liststore model"""
        for n, obj in enumerate(self.liststore_model):
            if obj[2] == bus_name_obj.bus_name_unique:
                del(self.liststore_model[n])
                break
    
    def __liststore_model_get(self, bus_name_obj):
        """get a object from the liststore"""
        for n, obj in enumerate(self.liststore_model):
            if obj[2] == bus_name_obj.bus_name_unique:
                return obj
        raise Exception("bus name object '%s' not found in liststore" % (bus_name_obj))


    def __name_owner_changed_cb(self, connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        """bus name added or removed"""
        bus_name = parameters[0]
        old_owner = parameters[1]
        new_owner = parameters[2]

        bus_name_obj = DBusBusName(bus_name)

        if bus_name[0] == ':':
            if not old_owner:
                self.__liststore_model_add(bus_name_obj)
            else:
                self.__liststore_model_remove(bus_name_obj)
        else :
            if new_owner:
                self.__liststore_model_add(bus_name_obj)
            if old_owner:
                self.__liststore_model_remove(bus_name_obj)


    def __list_names_handler(self, obj, names, userdata):
        for n in names:
            bus_name_obj = DBusBusName(n)
            self.__liststore_model_add(bus_name_obj)


    def __list_names_error_handler(self, obj, error, userdata):
        print "error getting bus names: %s" % str(error)


    def __get_unix_process_id_cb(self, obj, pid, bus_name_obj):
        bus_name_obj.pid = pid


    def __get_unix_process_id_error_cb(self, obj, error, bus_name_obj):
        print "error getting unix process id for %s: %s" % (bus_name_obj.bus_name_unique, str(error))
        bus_name_obj.pid = 0


    def __sort_on_name(self, model, iter1, iter2, user_data):
        un1 = model.get_value(iter1, 2)
        un2 = model.get_value(iter2, 2)

        # covert to integers if comparing two unique names
        if un1[0] == ':' and un2[0] == ':':
           un1 = un1[1:].split('.')
           un1 = tuple(map(int, un1))

           un2 = un2[1:].split('.')
           un2 = tuple(map(int, un2))

        elif un1[0] == ':' and un2[0] != ':':
            return 1
        elif un1[0] != ':' and un2[0] == ':':
            return -1
        else:
            un1 = un1.split('.')
            un2 = un2.split('.')

        if un1 == un2:
            return 0
        elif un1 > un2:
            return 1
        else:
            return -1


if __name__ == "__main__":
    """for debugging"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='show a given bus address')
    parser.add_argument('addr')
    p = parser.parse_args()

    if p.addr.lower() == 'system':
        addr = Gio.BusType.SYSTEM
    elif p.addr.lower() == 'session':
        addr = Gio.BusType.SESSION
    else:
        addr = p.addr

    bw = BusWatch(addr)

    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(1024, 768)
    win.add(bw.paned_buswatch)
    win.show_all()
    try:
        Gtk.main()
    except (KeyboardInterrupt, SystemExit):
        Gtk.main_quit()

        
