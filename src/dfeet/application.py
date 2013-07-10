# -*- coding: utf-8 -*-
from __future__ import print_function

from gi.repository import Gtk, Gio, GObject, Gdk

from dfeet.window import DFeetWindow


APP_MENU = """
<interface>
  <menu id='app-menu'>
    <section>
      <item>
        <attribute name='label' translatable='yes'>About</attribute>
        <attribute name='action'>app.about</attribute>
      </item>
      <item>
        <attribute name='label' translatable='yes'>Help</attribute>
        <attribute name='action'>app.help</attribute>
        <attribute name="accel">F1</attribute>
      </item>
      <item>
        <attribute name="label" translatable="yes">Quit</attribute>
        <attribute name="action">app.quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
      </item>
    </section>
  </menu>
</interface>
"""


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
        builder = Gtk.Builder()
        builder.add_from_string(APP_MENU)

        #create actions
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.action_about_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("help", None)
        action.connect("activate", self.action_help_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.action_quit_cb)
        self.add_action(action)

        self.set_app_menu(builder.get_object("app-menu"))

    def action_quit_cb(self, action, parameter):
        self.quit()

    def action_about_cb(self, action, parameter):
        aboutdialog = DFeetAboutDialog(self.package, self.version)
        aboutdialog.show()

    def action_help_cb(self, action, parameter):
        screen = Gdk.Screen.get_default()
        link = "help:d-feet"
        Gtk.show_uri(screen, link, Gtk.get_current_event_time())


class DFeetAboutDialog(Gtk.AboutDialog):
    def __init__(self, package, version):
        Gtk.AboutDialog.__init__(self)
        self.set_program_name(package)
        self.set_version(version)
        self.set_license_type(Gtk.License.GPL_2_0)
        self.set_website("https://wiki.gnome.org/DFeet/")
        self.set_logo_icon_name(package)
        self.connect("response", self.on_close_cb)

    def on_close_cb(self, action, parameter):
        action.destroy()
