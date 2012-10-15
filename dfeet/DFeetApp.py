# -*- coding: utf-8 -*-
from gi.repository import Gtk, Gio, GObject


from bus_watch import BusWatch
from settings import Settings
from _ui.uiloader import UILoader
from _ui.addconnectiondialog import AddConnectionDialog
from _ui.executemethoddialog import ExecuteMethodDialog


class NotebookTabLabel(Gtk.Box):
    __gsignals__ = {
        "close-clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    def __init__(self, label_text):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(5)
        # label 
        label = Gtk.Label(label_text)
        self.pack_start(label, True, True, 0)
        # close button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.connect("clicked", self.__button_clicked)
        self.pack_end(button, False, False, 0)
        self.show_all()
    
    def __button_clicked(self, button, data=None):
        self.emit("close-clicked")


class DFeetApp(Gtk.Application):

    HISTORY_MAX_SIZE = 10

    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.gnome.d-feet",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.connect("activate", self.on_application_activate_cb)

        signal_dict = {
            'action_systembus_connect_activate_cb': self.__systembus_connect_cb,
            'action_sessionbus_connect_activate_cb': self.__sessionbus_connect_cb,
            'action_otherbus_connect_activate_cb': self.__otherbus_connect_cb,
            'action_close_activate_cb': self.__close_cb,
            'action_about_activate_cb': self.__action_about_activate_cb,
            }

        settings = Settings.get_instance()

        ui = UILoader(UILoader.UI_MAINWINDOW) 
        self.main_window = ui.get_root_widget()
        self.main_window.connect('delete-event', self.__quit_dfeet)
        self.main_window.set_default_size(int(settings.general['windowwidth']), 
                                          int(settings.general['windowheight']))

        self.notebook = ui.get_widget('display_notebook')
        self.notebook.show_all()
        self.notebook_page_widget = ui.get_widget('box_notebook_page')
        self.about_dialog = ui.get_widget('aboutdialog')
        #create bus history list and load entries from settings
        self.__bus_history = []
        for bus in settings.general['addbus_list']:
            if bus != '':
                self.__bus_history.append(bus)

        ui.connect_signals(signal_dict)
        #add a System- and Session Bus tab
        self.__systembus_connect_cb(None)
        self.__sessionbus_connect_cb(None)


    def on_application_activate_cb(self, data=None):
        self.main_window.show()
        self.add_window(self.main_window)


    @property
    def bus_history(self):
        return self.__bus_history


    @bus_history.setter
    def bus_history(self, history_new):
        self.__bus_history = history_new


    def __systembus_connect_cb(self, action):
        """connect to system bus"""
        bw = BusWatch(Gio.BusType.SYSTEM)
        self.__notebook_append_page(bw.paned_buswatch, "System Bus")


    def __sessionbus_connect_cb(self, action):
        """connect to session bus"""
        bw = BusWatch(Gio.BusType.SESSION)
        self.__notebook_append_page(bw.paned_buswatch, "Session Bus")


    def __otherbus_connect_cb(self, action):
        """connect to other bus"""
        dialog = AddConnectionDialog(self.main_window, self.bus_history)
        result = dialog.run()
        if result == Gtk.ResponseType.OK:
            address = dialog.address
            if address == 'Session Bus':
                self.__sessionbus_connect_cb(None)
                return
            elif address == 'System Bus':
                self.__systembus_connect_cb(None)
                return
            else:
                try:
                    bw = BusWatch(address)
                    self.__notebook_append_page(bw.paned_buswatch, address)
                    # Fill history
                    if address in self.bus_history:
                        self.bus_history.remove(address)
                    self.bus_history.insert(0, address)
                    # Truncating history
                    if (len(self.bus_history) > self.HISTORY_MAX_SIZE):
                        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]
                except Exception as e:
                    print "can not connect to '%s': %s" % (address, str(e))
        dialog.destroy()


    def __action_about_activate_cb(self, action):
        """show the about dialog"""
        self.about_dialog.set_visible(True)
        self.about_dialog.run()
        self.about_dialog.set_visible(False)


    def __notebook_append_page(self, widget, text):
        """add a page to the notebook"""
        ntl = NotebookTabLabel(text)
        page_nbr = self.notebook.append_page(widget, ntl)
        ntl.connect("close-clicked", self.__notebook_page_close_clicked_cb, widget)


    def __notebook_page_close_clicked_cb(self, button, widget):
        """remove a page from the notebook"""
        nbr = self.notebook.page_num(widget)
        self.notebook.remove_page(nbr)


    def __close_cb(self, action):
        """quit program"""
        self.__quit_dfeet(self.main_window, None)


    def __quit_dfeet(self, main_window, event):
        """quit d-feet application and store some settings"""
        settings = Settings.get_instance()
        size = main_window.get_size()
        pos = main_window.get_position() 
    
        settings.general['windowwidth'] = size[0]
        settings.general['windowheight'] = size[1]

        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]

        settings.general['addbus_list'] = self.bus_history
        settings.write()
        self.quit()
