# -*- coding: utf-8 -*-
from __future__ import print_function

from gi.repository import Gtk, Gio, GObject

from dfeet.window import DFeetWindow


class DFeetApp(Gtk.Application):

    def __init__(self, package, version, data_dir):
        self.package = package
        self.version = version
        self.data_dir = data_dir
        Gtk.Application.__init__(self, application_id="org.gnome.d-feet",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)


    #Note that the function in C activate() becomes do_activate() in Python
    def do_activate(self):
        win = DFeetWindow(self, self.package, self.version, self.data_dir)

    #Note that the function in C startup() becomes do_startup() in Python
    def do_startup(self):
        Gtk.Application.do_startup(self)
