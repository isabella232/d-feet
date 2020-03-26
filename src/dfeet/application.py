# -*- coding: utf-8 -*-

from __future__ import print_function
from gi.repository import Gtk, Gio, GObject, Gdk, GLib
from dfeet.window import DFeetWindow
import gettext
import os

_ = gettext.gettext


def make_option(long_name, short_name=None, flags=0, arg=GLib.OptionArg.NONE,
                arg_data=None, description=None, arg_description=None):
    # surely something like this should exist inside PyGObject itself?!
    option = GLib.OptionEntry()
    option.long_name = long_name.lstrip('-')
    option.short_name = 0 if not short_name else short_name.lstrip('-')
    option.flags = flags
    option.arg = arg
    option.arg_data = arg_data
    option.description = description
    option.arg_description = arg_description
    return option


class DFeetApp(Gtk.Application):

    def __init__(self, package, version, data_dir):
        self.package = package
        self.version = version
        self.data_dir = data_dir
        Gtk.Application.__init__(self, application_id="org.gnome.dfeet",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.add_main_option_entries([
            make_option("--version", description=_("Show version number and exit")),
            make_option("--address", arg=GLib.OptionArg.STRING, arg_description="ADDRESS",
                        description=_("Open the specified bus address")),
        ])

    def do_handle_local_options(self, options):
        self.options = options
        if options.contains("version"):
            print(_("D-Feet version: {}").format(self.version))
            return 0
        return -1

    # Note that the function in C activate() becomes do_activate() in Python
    def do_activate(self):
        self._main_win = DFeetWindow(self, self.version, self.data_dir)
        if self.options.contains("address"):
            address = self.options.lookup_value("address").get_string()
            if not self._main_win.connect_to(address):
                self.quit()

    # Note that the function in C startup() becomes do_startup() in Python
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # create actions
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.action_about_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("help", None)
        action.connect("activate", self.action_help_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.action_quit_cb)
        self.add_action(action)

    def action_quit_cb(self, action, parameter):
        self.quit()

    def action_about_cb(self, action, parameter):
        aboutdialog = DFeetAboutDialog(self.package, self.version,
                                       self.props.application_id)
        aboutdialog.set_transient_for(self._main_win)
        aboutdialog.show()

    def action_help_cb(self, action, parameter):
        screen = Gdk.Screen.get_default()
        link = "help:d-feet"
        Gtk.show_uri(screen, link, Gtk.get_current_event_time())


class DFeetAboutDialog(Gtk.AboutDialog):
    def __init__(self, package, version, icon_name):
        Gtk.AboutDialog.__init__(self)
        self.set_program_name(_("D-Feet"))
        self.set_version(version)
        self.set_license_type(Gtk.License.GPL_2_0)
        self.set_website("https://wiki.gnome.org/Apps/DFeet/")
        self.set_logo_icon_name(icon_name)
        self.connect("response", self.on_close_cb)

    def on_close_cb(self, action, parameter):
        action.destroy()
