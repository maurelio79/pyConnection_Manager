#!/usr/bin/env python
# -*- coding: utf-8; -*-

from gi.repository import Gtk, Gdk, Vte, GLib, Pango, GConf, GdkPixbuf
import json, os, getpass, sqlite3
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


class PyCmError(Gtk.Dialog):
    """The About pyConnection Manager dialog class
    """
    def __init__(self, error):

        super(PyCmError, self).__init__()

        self.error = error

        self.builder_error = Gtk.Builder()  
        self.builder_error.add_from_file(gladefile('pycm_error.glade'))

        self.w_error = self.builder_error.get_object('window-error')
        self.label_error = self.builder_error.get_object('label-error')
        self.button_error = self.builder_error.get_object('button-error')

        signals = {
            "on_button-error_clicked" : lambda _: self.destroy(),
        }

        self.builder_error.connect_signals(signals)

        self.w_error.connect('destroy', lambda _: self.destroy())

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        self.w_error.set_icon(self.img)

        self.label_error.set_text(self.error)

        self.w_error.show_all()




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
    """This class manage user preferences stored in gconf file.
        The class load preference into the preference gui when the user call it;
        and also save prefernce when user chenge them.
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

        

        # Get all object for prefs window.        

        self.filechooserbutton = self.builder_prefs.get_object('filechooserbutton')
        self.entry_user = self.builder_prefs.get_object('entry-user')
        self.bg_colorbutton = self.builder_prefs.get_object('bg-colorbutton')
        self.fg_colorbutton = self.builder_prefs.get_object('fg-colorbutton')
        self.font_button = self.builder_prefs.get_object('font-button')
        self.hscale_opacity = self.builder_prefs.get_object('hscale-opacity')
        self.shellcombo = self.builder_prefs.get_object('shell_combo')
        self.spin_scrollback = self.builder_prefs.get_object('spin-scrollback')
        self.switch_vbar = self.builder_prefs.get_object('switch-vbar')
        self.entry_command = self.builder_prefs.get_object('entry-command')
        self.switch_fullscreen = self.builder_prefs.get_object('switch-fullscreen')
        self.button_save = self.builder_prefs.get_object('button-save')
        

        home = os.getenv('HOME')
        conf = '.gconf/apps/pycm'
        gconf_dir = os.path.join(home, conf)
        
        if os.path.exists(gconf_dir):

                # Object from window tab

            self.entry_user_text = self.client.get_string(KEY('/general/default_user'))
            if self.entry_user_text != None:
                self.entry_user.set_text(self.entry_user_text)

                # Object from style and apparence tab
            
            self.bg_colorbutton_color = Gdk.color_parse(self.client.get_string(KEY('/style/background/color')))
            if self.bg_colorbutton_color != None:
                self.bg_colorbutton.set_color(self.bg_colorbutton_color)

            self.fg_colorbutton_color = Gdk.color_parse(self.client.get_string(KEY('/style/font/color')))
            if self.fg_colorbutton_color != None:
                self.fg_colorbutton.set_color(self.fg_colorbutton_color)
            
            self.font_button_font = self.client.get_string(KEY('/style/font/style'))
            if self.font_button_font != None:
                self.font_button.set_font_name(self.font_button_font)
            
            self.opacity_value = self.client.get_int(KEY('/style/background/transparency'))
            if self.opacity_value != None:
                self.hscale_opacity.set_value(self.opacity_value)


                # Object from terminal tab
            
            self.load_shells_combo()
            self.shellvalue_id = self.client.get_int(KEY('/general/default_shell_id'))
            if self.shellvalue_id != None:
                self.shellcombo.set_active(self.shellvalue_id)

            self.scrollback_lines = self.client.get_int(KEY('/general/scrollback'))
            if self.scrollback_lines != None:
                self.spin_scrollback.set_value(self.scrollback_lines)
            
            self.vbar_bool = self.client.get_bool(KEY('/general/vbar'))
            if self.vbar_bool != None:
                self.switch_vbar.set_active(self.vbar_bool)
            
            self.command = self.client.get_string(KEY('/general/command'))
            if self.command is not None:
                self.entry_command.set_text(self.command)
            
            self.fullscreen_bool = self.client.get_bool(KEY('/general/fullscreen'))
            if self.fullscreen_bool != None:
                self.switch_fullscreen.set_active(self.fullscreen_bool)

        else:
            pass

        
        
        signals = {
            "on_window-prefs_destroy" : self.delete,
            "on_button-save_clicked" : self.delete,
            "on_bg-colorbutton_color_set" : self.set_bg,
            "on_fg-colorbutton_color_set" : self.set_fg,
            "on_font-button_font_set" : self.set_font,
            "on_hscale-opacity_value_changed" : self.set_opacity,
            "on_shell_combo_changed" : self.set_shell,
            "on_spin-scrollback_value_changed" : self.set_scrollback,
            "on_switch-vbar_toggled" : self.set_vbar,
            "on_switch-fullscreen_toggled" : self.set_fullscreen,
            "on_button-command_clicked" : self.set_command,
            "on_button-user_clicked" : self.set_user,
        }

        self.builder_prefs.connect_signals(signals)

        self.w_prefs.show_all()

    def delete(self, widget):
        self.w_prefs.destroy()


    # All function above just write value in gconf file when user change preference.

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
        print self.opacity
        self.client.set_int(KEY('/style/background/transparency'), self.opacity)

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

        # I will also save the id of shell to easily load then in the combo box
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

    def set_fullscreen(self, widget):
        self.is_fullscreen = self.switch_fullscreen.get_active()
        self.client.set_bool(KEY('/general/fullscreen'), self.is_fullscreen)

    def set_command(self, widget):
        self.command = self.entry_command.get_text()
        self.client.set_string(KEY('/general/command'), self.command)

    def set_user(self, widget):
        self.default_user = self.entry_user.get_text()
        self.client.set_string(KEY('/general/default_user'), self.default_user)




class PycmNew(Gtk.Window):
    """docstring for PycmNew"""

    def __init__(self):
        super(PycmNew, self).__init__()

        self.builder_new = Gtk.Builder() 
        self.builder_new.add_from_file(gladefile('pycm_new.glade'))

        self.w_new = self.builder_new.get_object('window-new')

        self.button_db = self.builder_new.get_object('button-db')
        self.entry_db = self.builder_new.get_object('entry-db')

        signals = {
            "on_button-db_clicked" : self.save_db,


        }

        self.w_new.connect('destroy', lambda _: self.destroy())

        self.builder_new.connect_signals(signals)

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        self.w_new.set_icon(self.img)

        self.w_new.show_all()

    def save_db(self, widget):
        
        self.db_name = self.entry_db.get_text()

        DB_PATH = '/home/'+ USERNAME + '/.pycm'

        self.db_name_full = DB_PATH + "/pycm.db"
        if not os.path.exists(DB_PATH):
            os.system("mkdir " + DB_PATH)
        print DB_PATH
        try:
            db = sqlite3.connect(self.db_name_full)

            query = """CREATE TABLE `%s` (
               `id` integer primary key autoincrement,
               `full_name` char(255) not null,
               `display_name` char(255),
               `ip_address` char(255) not null,
               `user`  char(255) not null
            );""" % (self.db_name)

            db.execute(query)
            db.commit()
            db.close()
        except sqlite3.OperationalError as e:
            PyCmError(str(e))
        


class GConfHandler(object):
    """Handles gconf changes, if any gconf variable is changed, a
    different method is called to handle this change.
    """
    def __init__(self, window, term):
        """Constructor of GConfHandler, just add the term dir to the
        gconf client and bind the keys to its handler methods.
        """
        self.term = term
        self.window = window

        client = GConf.Client.get_default()
        client.add_dir(GCONF_PATH, GConf.ClientPreloadType.PRELOAD_RECURSIVE)

        notify_add = client.notify_add

        notify_add(KEY('/style/font/style'), self.fstyle_changed, None)
        notify_add(KEY('/style/font/color'), self.fcolor_changed, None)
        notify_add(KEY('/style/background/color'), self.bgcolor_changed, None)
        notify_add(KEY('/style/background/transparency'), self.opacity_changed, None)
        notify_add(KEY('/general/scrollback'), self.scrollback_changed, None)
        notify_add(KEY('/general/vbar'), self.vbar_changed, None)

    # All function below, change immediately style, apparence, ecc of main window and terminal.

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
        self.window.set_opacity((100 - opacity) / 100.0)
        


    def scrollback_changed(self, client, connection_id, entry, data):
        
        lines = client.get_int(KEY('/general/scrollback'))
        for i in term_list:
            i.set_scrollback_lines(lines)

    def vbar_changed(self, client, connection_id, entry, data):
        vbar = client.get_bool(KEY('/general/vbar'))
        for i in term_list:
            hbox = i.get_parent()
            terminal, scrollbar = hbox.get_children()
            if vbar == True:
                scrollbar.show()
            else:
                scrollbar.hide()
        



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




class PyCmBoxTerminal(Gtk.HBox):
    """Create a box container for terminal. I need this in case user wants to add a scrollbar
    """
    def __init__(self):
        
        super(PyCmBoxTerminal, self).__init__()

        self.term = PyCmTerminal()
        self.add_terminal()
        self.add_scrollbar()

    def add_terminal(self):
        self.pack_start(self.term, True, True, 0)

    def add_scrollbar(self):
        adj = self.term.get_vadjustment()
        self.scroll = Gtk.VScrollbar(adj)
        self.scroll.set_no_show_all(True)
        self.pack_start(self.scroll, False, False, 0)




class PyCm(object):
    """Main class for application
    """
    def __init__(self):

        super(PyCm, self).__init__()

        #self.term = PyCmTerminal()
        self.client = GConf.Client.get_default()

        builder = Gtk.Builder()  
        builder.add_from_file(gladefile('pycm.glade'))

        w = builder.get_object('window-root')

        # images
        self.ipath = pixmapfile('utilities-terminal.png')
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.ipath)
        w.set_icon(self.img)


        self.hbox = PyCmBoxTerminal()
        self.hpaned = builder.get_object('hpaned')
        self.notebook = builder.get_object('notebook')


        signals = {
            "on_window-root_destroy" : Gtk.main_quit,
            "on_quit_activate" : Gtk.main_quit,
            "on_preference_activate" : self.show_prefs,
            "on_new-tab_clicked" : self.add_tab,
            "on_about_activate" : self.show_about,
            "on_open_activate" : self.show_open_file,
            "on_new_activate" : self.show_new_file,
        }

        builder.connect_signals(signals)

        #self.term = Vte.Terminal()
        #self.term.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], ["/bin/bash"], 
        #                           [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)

        self.hbox.term.connect("child-exited", Gtk.main_quit)

        self.tab_label = Gtk.Label(USERNAME + "@" + HOSTNAME)

        self.notebook.append_page(self.hbox, self.tab_label)

        self.current_tab = self.notebook.get_current_page()

        self.notebook.next_page()

        GConfHandler(w, self.hbox.term)

        self.fullscreen = self.client.get_bool(KEY('/general/fullscreen'))
        if self.fullscreen:
            w.fullscreen()

        self.opacity = self.client.get_int(KEY('/style/background/transparency'))
        w.set_opacity((100 - self.opacity) / 100.0)

        w.show_all()
        self.hbox.term.grab_focus()

        self.load_config()
        term_list.append(self.hbox.term)


    def load_config(self):
        """Function that load configuration for Vte at startup
        """
        # Colors need to after window show!!
        
        
        try:
            self.shellvalue = self.client.get_string(KEY('/general/default_shell'))
            if not self.shellvalue or self.shellvalue == "":
                self.shellvalue = "/bin/bash"
            self.hbox.term.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], [self.shellvalue], 
                    [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)
        except:
            print "Could not load shell type! Big problem!"

        try:
            self.bgcolor = Gdk.color_parse(self.client.get_string(KEY('/style/background/color')))
            self.hbox.term.set_color_background(self.bgcolor)
            self.hbox.term.set_background_tint_color(self.bgcolor)
            self.fgcolor = Gdk.color_parse(self.client.get_string(KEY('/style/font/color')))
            self.hbox.term.set_color_foreground(self.fgcolor)
            self.font = Pango.FontDescription(self.client.get_string(KEY('/style/font/style')))
            self.hbox.term.set_font(self.font)
            #self.opacity = self.client.get_int(KEY('/style/background/transparency'))
            #self.hbox.term.set_opacity(self.opacity)
            self.lines = self.client.get_int(KEY('/general/scrollback'))
            self.hbox.term.set_scrollback_lines(self.lines)
            self.command = self.client.get_string(KEY('/general/command'))
            if self.command != "":
                self.length_command = len(self.command) + 1
                self.hbox.term.feed_child(self.command + "\n", self.length_command)
            self.scrollbar = self.client.get_bool(KEY('/general/vbar'))
            if self.scrollbar:
                self.hbox.scroll.show()
            else:
                self.hbox.scroll.hide()            
        except:
            print "I can't load user preference. I will load a basic standard terminal."

    def show_prefs(self, widget):
        """Show preference window
        """
        PyCmPrefs()

    def show_about(self, widget):
        """Show about dialog
        """
        PyCmAbout()

    def show_open_file(self, widget):
        """Show open file dialog
        """
        self.builder_open = Gtk.Builder()  
        self.builder_open.add_from_file(gladefile('pycm_open.glade'))

        self.w_open = self.builder_open.get_object('filechooser-dialog')
        

        signals = {
            "on_button-cancel_clicked" : self.delete_open,
            "on_button-ok_clicked" : self.load_file,
        }

        self.builder_open.connect_signals(signals)

        self.w_open.show_all()

    def show_new_file(self, widget):
        PycmNew()

    # def load_file(self, widget):
    #     """Load file in the TreeView
    #     """
    #     self.serverfile = self.w_open.get_filename()

    #     if self.serverfile is not "None":
    #         self.delete_open(self)
    #         self.treestore = Gtk.TreeStore(str)

    #         with open(self.serverfile) as data_file:
    #             self.data = json.load(data_file)

    #         for i in self.data:
    #             self.piter = self.treestore.append(None, [i])
    #             for j in self.data[i]:
    #                 self.treestore.append(self.piter, [j])
            
    #         # create the TreeView using treestore
    #         self.treeview = Gtk.TreeView(self.treestore)

    #         # create the TreeViewColumn to display the data
    #         self.tvcolumn = Gtk.TreeViewColumn('Server List')

    #         # add tvcolumn to treeview
    #         self.treeview.append_column(self.tvcolumn)

    #         # create a CellRendererText to render the data
    #         self.cell = Gtk.CellRendererText()
    #         #self.cell.set_property('editable', True)
            
    #         # add the cell to the tvcolumn and allow it to expand
    #         self.tvcolumn.pack_start(self.cell, True)

    #         # set the cell "text" attribute to column 0 - retrieve text
    #         # from that column in treestore
    #         self.tvcolumn.add_attribute(self.cell, 'text', 0)

    #         # make it searchable
    #         self.treeview.set_search_column(0)

    #         # Allow sorting on the column
    #         self.tvcolumn.set_sort_column_id(0)

    #         # Allow drag and drop reordering of rows
    #         self.treeview.set_reorderable(True)

    #         self.hpaned.add2(self.treeview)
    #         self.treeview.show()

    #         # Signal for tree view goes here
    #         self.treeview.connect("row-activated", self.add_remote_tab)

    def delete_open(self, widget):
        """Delete open file dialog
        """
        self.w_open.destroy()


    def add_tab(self, widget):
        """New terminal when user click on button New
        """
        self.hbox = PyCmBoxTerminal()

        self.hbox.term.connect("child-exited", self.remove_tab)

        self.tab_label = Gtk.Label(USERNAME + "@" + HOSTNAME)

        self.notebook.append_page(self.hbox, self.tab_label)
        self.current_tab = self.notebook.get_current_page()

        self.hbox.term.show()
        self.hbox.show()        

        self.notebook.next_page()

        self.hbox.term.grab_focus()

        self.load_config()

        term_list.append(self.hbox.term)


    def add_remote_tab(self, widget, item, obj):
        """New terminal when user click on a server name in the
            treeview
        """
        self.treeselection = self.treeview.get_selection()
        print self.treeselection
        (self.model, self.pathlist) = self.treeselection.get_selected_rows()

        for path in self.pathlist :
            self.tree_iter = self.model.get_iter(path)
            self.host = self.model.get_value(self.tree_iter,0)
            self.parent = self.model.iter_parent(self.tree_iter)
            self.parent_value = self.model.get_value(self.parent, 0)

        self.hbox = PyCmBoxTerminal()

        self.hbox.term.connect("child-exited", self.remove_tab)

        self.default_user = self.client.get_string(KEY('/general/default_user'))

        if self.default_user != None:
            self.user = self.default_user
        else:
            self.user = USERNAME        

        self.tab_label = Gtk.Label(self.user + "@" + self.host)

        self.notebook.append_page(self.hbox, self.tab_label)
        self.current_tab = self.notebook.get_current_page()

        self.hbox.term.show()
        self.hbox.show()        
        self.notebook.next_page()
        self.hbox.term.grab_focus()

        self.load_config()

        self.command = 'ssh ' + self.user + "@" + self.data[self.parent_value][self.host]
        self.length_command = len(self.command) + 1
        self.hbox.term.feed_child(self.command + "\n", self.length_command)

        term_list.append(self.hbox.term)


    def remove_tab(self, widget):

        self.current_tab = self.notebook.get_current_page()
        term_list.pop(self.current_tab)
        self.notebook.remove_page(self.current_tab)

    def main(self):
        Gtk.main()


if __name__ == "__main__":
    pycm = PyCm()
    pycm.main()