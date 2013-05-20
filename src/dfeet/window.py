# -*- coding: utf-8 -*-
# Copyright (C) 2013 Thomas Bechtold <thomasbechtold@jpberlin.de>

# This file is part of D-Feet.

# D-Feet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# D-Feet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with D-Feet.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk, Gio

import gettext
from gettext import gettext as _
gettext.textdomain('d-feet')

from dfeet.bus_watch import BusWatch
from dfeet.settings import Settings
from dfeet.uiloader import UILoader
from dfeet.addconnectiondialog import AddConnectionDialog
from dfeet.executemethoddialog import ExecuteMethodDialog


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


class DFeetWindow(Gtk.ApplicationWindow):
    """the main window"""

    HISTORY_MAX_SIZE = 10

    def __init__(self, app, package, version, data_dir):
        Gtk.Window.__init__(self, application=app)
        self.package = package
        self.version = version
        self.data_dir = data_dir
        #setup the window
        self.set_default_size(600, 480)
        self.set_title(self.package)
        self.set_icon_name(package)

        signal_dict = {
            'action_systembus_connect_activate_cb': self.__systembus_connect_cb,
            'action_sessionbus_connect_activate_cb': self.__sessionbus_connect_cb,
            'action_otherbus_connect_activate_cb': self.__otherbus_connect_cb,
            'action_close_activate_cb': self.__close_cb,
            }

        #get settings
        settings = Settings.get_instance()

        ui = UILoader(self.data_dir, UILoader.UI_MAINWINDOW)
        vbox1 = ui.get_widget('vbox1')
        self.add(vbox1)
        self.connect('delete-event', self.__quit_dfeet)
        self.set_default_size(int(settings.general['windowwidth']),
                              int(settings.general['windowheight']))

        self.notebook = ui.get_widget('display_notebook')
        self.notebook.show_all()
        self.notebook_page_widget = ui.get_widget('box_notebook_page')
        #create bus history list and load entries from settings
        self.__bus_history = []
        for bus in settings.general['addbus_list']:
            if bus != '':
                self.__bus_history.append(bus)

        ui.connect_signals(signal_dict)
        #add a System- and Session Bus tab
        self.__systembus_connect_cb(None)
        self.__sessionbus_connect_cb(None)

        self.show_all()

    @property
    def bus_history(self):
        return self.__bus_history

    @bus_history.setter
    def bus_history(self, history_new):
        self.__bus_history = history_new

    def __systembus_connect_cb(self, action):
        """connect to system bus"""
        try:
            bw = BusWatch(self.data_dir, Gio.BusType.SYSTEM)
            self.__notebook_append_page(bw.paned_buswatch, "System Bus")
        except Exception as e:
            print(e)

    def __sessionbus_connect_cb(self, action):
        """connect to session bus"""
        try:
            bw = BusWatch(self.data_dir, Gio.BusType.SESSION)
            self.__notebook_append_page(bw.paned_buswatch, "Session Bus")
        except Exception as e:
            print(e)

    def __otherbus_connect_cb(self, action):
        """connect to other bus"""
        dialog = AddConnectionDialog(self.data_dir, self, self.bus_history)
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
                    bw = BusWatch(self.data_dir, address)
                    self.__notebook_append_page(bw.paned_buswatch, address)
                    # Fill history
                    if address in self.bus_history:
                        self.bus_history.remove(address)
                    self.bus_history.insert(0, address)
                    # Truncating history
                    if (len(self.bus_history) > self.HISTORY_MAX_SIZE):
                        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]
                except Exception as e:
                    print("can not connect to '%s': %s" % (address, str(e)))
        dialog.destroy()

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
        self.__quit_dfeet(self, None)

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
