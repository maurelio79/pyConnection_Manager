#!/usr/bin/env python
# -*- coding: utf-8; -*-

from gi.repository import Gtk, Gdk, Vte, GLib, Pango, GConf, GdkPixbuf
import json, os, getpass
import sys
sys.path.append('/usr/lib/python2.7/dist-packages/pycm/')
from pycm_globals import *


def gladefile(x):
    f = os.path.join(GLADE_DIR, x)
    if not os.path.exists(f):
        raise IOError('No such file or directory: %s' % f)
    return os.path.abspath(f)

def pixmapfile(x):
    f = os.path.join(IMAGE_DIR, x)
    if not os.path.exists(f):
        raise IOError('No such file or directory: %s' % f)
    return os.path.abspath(f)

def hexify_color(c):
    h = lambda x: hex(x).replace('0x', '').zfill(4)
    return '#%s%s%s' % (h(c.red), h(c.green), h(c.blue))



term_list = []



class PyCmAbout(Gtk.AboutDialog):
    """The About pyConnection Manager dialog class
    """
    def __init__(self):

        super(PyCmAbout, self).__init__()

        self.builder_about = Gtk.Builder()  
        self.builder_about.add_from_file(gladefile('pycm_about.glade'))

        self.w_about = self.builder_about.get_object('aboutdialog')

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        self.w_about.set_property('logo', self.img)

        self.w_about.set_name('pyConnection Manager')
        self.w_about.set_version(VERSION)

        signals = {
            "on_aboutdialog-action_area2_delete_event" : self.delete,
            "on_aboutdialog-action_area2_destroy_event" : self.delete,
            "on_aboutdialog_delete_event" : self.delete,
            "on_aboutdialog_destroy_event" : self.delete,
            "on_aboutdialog_response" : self.delete,
        }

        self.builder_about.connect_signals(signals)

        self.w_about.show_all()
    

    def delete(self, widget, response):
        self.w_about.destroy()


class PyCmPrefs(Gtk.Window):
    """This class manage user preferences stored in prefs.json
        The class load preference into the preference gui when the user call it;
        load preference for the PyCm main class;
        and save preference in prefs.json.
    """

    def __init__(self):

        super(PyCmPrefs, self).__init__()

        self.client = GConf.Client.get_default()

        self.builder_prefs = Gtk.Builder() 
        self.builder_prefs.add_from_file(gladefile('pycm_prefs.glade'))

        self.w_prefs = self.builder_prefs.get_object('window-prefs')

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        self.w_prefs.set_icon(self.img)

        # Get all object for prefs window

            # Object from pycm tab
        self.filechooserbutton = self.builder_prefs.get_object('filechooserbutton')
        #self.entry_user = self.builder_prefs.get_object('entry-user')

            # Object from style and apparence tab
        self.bg_colorbutton = self.builder_prefs.get_object('bg-colorbutton')
        self.fg_colorbutton = self.builder_prefs.get_object('fg-colorbutton')
        self.font_button = self.builder_prefs.get_object('font-button')
        #self.hscale_opacity = self.builder_prefs.get_object('hscale-opacity')

            # Object from terminal tab
        self.shellcombo = self.builder_prefs.get_object('shell_combo')
        self.spin_scrollback = self.builder_prefs.get_object('spin-scrollback')
        self.switch_vbar = self.builder_prefs.get_object('switch-vbar')
        self.entry_command = self.builder_prefs.get_object('entry-command')

        self.button_save = self.builder_prefs.get_object('button-save')



        
        # Load object value from gconf file into pref object

            # Load value for object in style and apparence tab
        self.bg_colorbutton_color = Gdk.color_parse(self.client.get_string(KEY('/style/background/color')))
        self.bg_colorbutton.set_color(self.bg_colorbutton_color)
        self.fg_colorbutton_color = Gdk.color_parse(self.client.get_string(KEY('/style/font/color')))
        self.fg_colorbutton.set_color(self.fg_colorbutton_color)
        self.font_button_font = self.client.get_string(KEY('/style/font/style'))
        self.font_button.set_font_name(self.font_button_font)
        self.opacity_value = self.client.get_int(KEY('/style/background/transparency'))
        #self.hscale_opacity.set_value(int(self.opacity_value))

            # Load value for object in terminal tab
        self.load_shells_combo()
        self.shellvalue_id = self.client.get_int(KEY('/general/default_shell_id'))
        self.shellcombo.set_active(self.shellvalue_id)
        self.scrollback_lines = self.client.get_int(KEY('/general/scrollback'))
        self.spin_scrollback.set_value(self.scrollback_lines)
        self.vbar_bool = self.client.get_bool(KEY('/general/vbar'))
        self.switch_vbar.set_active(self.vbar_bool)
        self.command = self.client.get_string(KEY('/general/command'))
        if self.command is not None:
            self.entry_command.set_text(self.command)


        signals = {
            "on_window-prefs_destroy" : self.delete,
            "on_button-save_clicked" : self.delete,
            "on_bg-colorbutton_color_set" : self.set_bg,
            "on_fg-colorbutton_color_set" : self.set_fg,
            "on_font-button_font_set" : self.set_font,
            #"on_hscale-opacity_value_changed" : self.set_opacity,
            "on_shell_combo_changed" : self.set_shell,
            "on_spin-scrollback_value_changed" : self.set_scrollback,
            "on_switch-vbar_activate" : self.set_vbar,
            "on_button-command_clicked" : self.set_command,
        }

        self.builder_prefs.connect_signals(signals)

        self.w_prefs.show_all()

    def delete(self, widget):
        self.w_prefs.destroy()


    def set_bg(self, widget):
        self.color = hexify_color(self.bg_colorbutton.get_color())
        self.client.set_string(KEY('/style/background/color'), self.color)

    def set_fg(self, widget):
        self.color = hexify_color(self.fg_colorbutton.get_color())
        self.client.set_string(KEY('/style/font/color'), self.color)

    def set_font(self, widget):
        self.font = self.font_button.get_font_name()
        self.client.set_string(KEY('/style/font/style'), self.font)

    def set_opacity(self, widget):
        self.opacity = self.hscale_opacity.get_value()
        self.client.set_int(KEY('/style/background/transparency'), int(self.opacity))

    def set_shell(self, widget):
        self.citer = self.shellcombo.get_active_iter()
        if not self.citer:
            return
        self.shell = self.shellcombo.get_model().get_value(self.citer, 0)
        # we unset the value (restore to default) when user chooses to use
        # user shell as guake shell interpreter.
        #if shell == USER_SHELL_VALUE:
        #    self.client.unset(KEY('/general/default_shell'))
        #else:
        self.client.set_string(KEY('/general/default_shell'), self.shell)

        # I will also save the id of shell to easily load then in the gui
        self.shell_id = self.shellcombo.get_active()
        self.client.set_int(KEY('/general/default_shell_id'), int(self.shell_id))

    def load_shells_combo(self):
        # append user shell as first option
        #self.shellcombo.append_text(USER_SHELL_VALUE)
        if os.path.exists(SHELLS_FILE):
            lines = open(SHELLS_FILE).readlines()
            for i in lines:
                possible = i.strip()
                if possible and not possible.startswith('#') and \
                   os.path.exists(possible):
                    self.shellcombo.append_text(possible)

    def set_scrollback(self, widget):
        self.scrollback_lines = self.spin_scrollback.get_value() 
        self.client.set_int(KEY('/general/scrollback'), self.scrollback_lines)

    def set_vbar(self, widget):
        self.use_vbar = self.switch_vbar.get_active()
        self.client.set_bool(KEY('/general/vbar'), self.use_vbar)

    def set_command(self, widget):
        self.command = self.entry_command.get_text()
        self.client.set_string(KEY('/general/command'), self.command)




class GConfHandler(object):
    """Handles gconf changes, if any gconf variable is changed, a
    different method is called to handle this change.
    """
    def __init__(self, term):
        """Constructor of GConfHandler, just add the term dir to the
        gconf client and bind the keys to its handler methods.
        """
        self.term = term

        client = GConf.Client.get_default()
        client.add_dir(GCONF_PATH, GConf.ClientPreloadType.PRELOAD_RECURSIVE)

        notify_add = client.notify_add

        notify_add(KEY('/style/font/style'), self.fstyle_changed, None)
        notify_add(KEY('/style/font/color'), self.fcolor_changed, None)
        notify_add(KEY('/style/background/color'), self.bgcolor_changed, None)
        #notify_add(KEY('/style/background/transparency'), self.opacity_changed, None)
        notify_add(KEY('/general/scrollback'), self.scrollback_changed, None)
        notify_add(KEY('/general/vbar'), self.vbar_changed, None)

    def fstyle_changed(self, client, connection_id, entry, data):
        """If the gconf var style/font/style be changed, this method
        will be called and will change the font style in all terminals
        open.
        """
        font = Pango.FontDescription(client.get_string(KEY('/style/font/style')))
        for i in term_list:
            i.set_font(font)

    def bgcolor_changed(self, client, connection_id, entry, data):

        bgcolor = Gdk.color_parse(client.get_string(KEY('/style/background/color')))
        for i in term_list:
            i.set_color_background(bgcolor)
            i.set_background_tint_color(bgcolor)

    def fcolor_changed(self, client, connection_id, entry, data):

        fgcolor = Gdk.color_parse(client.get_string(KEY('/style/font/color')))
        for i in term_list:
            i.set_color_foreground(fgcolor)

    def opacity_changed(self, client, connection_id, entry, data):
        opacity = client.get_int(KEY('/style/background/transparency'))
        for i in term_list:
            i.set_opacity(opacity)

    def scrollback_changed(self, client, connection_id, entry, data):
        
        lines = client.get_int(KEY('/general/scrollback'))
        for i in term_list:
            i.set_scrollback_lines(lines)

    def vbar_changed(self, client, connection_id, entry, data):
    #    vbar = client.get_bool('/general/vbar')
    #    for i in term.term_list:
    #        hbox = i.get_parent()
    #        terminal, scrollbar = hbox.get_children()
    #        if entry.value.get_bool():
    #            scrollbar.show()
    #        else:
    #            scrollbar.hide()
        pass




class PyCmTerminal(Vte.Terminal):
    """Just create a standard terminal with some configuration
    """
    def __init__(self):

        super(PyCmTerminal, self).__init__()
        self.configure_terminal()

    def configure_terminal(self):
        client = GConf.Client.get_default()
        self.set_audible_bell(False)
        self.set_visible_bell(False)
        self.set_sensitive(True)
        #self.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], ["/bin/bash"], 
        #            [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)




class PyCm(object):
    """Main class for application
    """
    def __init__(self):

        super(PyCm, self).__init__()

        self.term = PyCmTerminal()
        self.client = GConf.Client.get_default()

        builder = Gtk.Builder()  
        builder.add_from_file(gladefile('pycm.glade'))

        w = builder.get_object('window-root')

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        w.set_icon(self.img)

        self.entry_user = builder.get_object('entry_user')

        self.notebook = builder.get_object('notebook')


        signals = {
            "on_window-root_destroy" : Gtk.main_quit,
            "on_quit_activate" : Gtk.main_quit,
            "on_preference_activate" : self.show_prefs,
            "on_new-tab_clicked" : self.add_tab,
            "on_about_activate" : self.show_about,
        }

        builder.connect_signals(signals)

        #self.term = Vte.Terminal()
        #self.term.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], ["/bin/bash"], 
        #                           [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)

        self.term.connect("child-exited", Gtk.main_quit)

        self.tab_label = Gtk.Label(USERNAME + "@" + HOSTNAME)

        
        self.notebook.append_page(self.term, self.tab_label)
        self.current_tab = self.notebook.get_current_page()

        self.notebook.next_page()

        GConfHandler(self.term)

        w.show_all()
        self.term.grab_focus()
        self.load_config()
        term_list.append(self.term)


    def load_config(self):
        """Function that load configuration for Vte at startup
        """
        # Colors need to after window show!!
        try:
            self.shellvalue = self.client.get_string(KEY('/general/default_shell'))
            if self.shellvalue == "":
                self.shellvalue = "/bin/bash"
            self.term.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], [self.shellvalue], 
                    [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)
        except:
            print "Could not load shell type! Big problem!"

        try:
            self.bgcolor = Gdk.color_parse(self.client.get_string(KEY('/style/background/color')))
            self.term.set_color_background(self.bgcolor)
            self.term.set_background_tint_color(self.bgcolor)
            self.fgcolor = Gdk.color_parse(self.client.get_string(KEY('/style/font/color')))
            self.term.set_color_foreground(self.fgcolor)
            self.font = Pango.FontDescription(self.client.get_string(KEY('/style/font/style')))
            self.term.set_font(self.font)
            #self.opacity = self.client.get_int(KEY('/style/background/transparency'))
            #self.term.set_opacity(self.opacity)
            self.lines = self.client.get_int(KEY('/general/scrollback'))
            self.term.set_scrollback_lines(self.lines)
            self.command = self.client.get_string(KEY('/general/command'))
            if self.command != "":
                self.length_command = len(self.command) + 1
                self.term.feed_child(self.command + "\n", self.length_command)
            
        except:
            print "I can't load user preference. I will load a basic standard terminal."

    def show_prefs(self, widget):
        """Load preference window
        """
        PyCmPrefs()

    def show_about(self, widget):
        """Load about dialog
        """
        PyCmAbout()


    def add_tab(self, widget):
        """New terminal when user click on button New
        """
        self.term = PyCmTerminal()

        self.term.connect("child-exited", self.remove_tab)

        self.tab_label = Gtk.Label(USERNAME + "@" + HOSTNAME)

        self.notebook.append_page(self.term, self.tab_label)
        self.current_tab = self.notebook.get_current_page()

        self.term.show()

        self.load_config()

        self.notebook.next_page()

        self.term.grab_focus()

        term_list.append(self.term)

    def remove_tab(self, widget):

        self.current_tab = self.notebook.get_current_page()
        self.notebook.remove_page(self.current_tab)

    def main(self):
        Gtk.main()


if __name__ == "__main__":
    pycm = PyCm()
    pycm.main()