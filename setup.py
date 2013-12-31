#!/usr/bin/env python
import sys, shutil

try:
    from gi.repository import Gtk, Gdk, Vte, GLib, Pango, GConf, GdkPixbuf
    import json, os, getpass
    from pycm.pycm_globals import *
except ImportError as e:
    print "Error during importing of necessaries modules.\nError is '%s'" % e
    sys.exit()


python_path = "/usr/lib/python2.7/dist-packages/"
module_path = python_path + 'pycm'
bin_exe = '/usr/bin/pycm.py'
launcher = '/usr/share/applications/pyconnection-manager.desktop'
uid = os.getuid()


def __init__():
    if uid > 0:
        print "You need to be root to install pyConnection Manager"
        sys.exit()

    try:
        remove_old()
    except OSError, IOError:
        print "ERROR removing old stuff"
        sys.exit()

    try:
        create_new()
    except OSError, IOError:
        print "ERROR installing pyConnection Manager"
        sys.exit()

    ok = "\n\tpyConnection Manager succesfully installed\n"
    print ok

def remove_old():
    if os.path.exists(module_path):
        shutil.rmtree(module_path)

    if os.path.exists(GLADE_DIR):
        shutil.rmtree(GLADE_DIR)

    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)

    if os.path.exists(bin_exe):
        os.remove(bin_exe)

    if os.path.exists(launcher):
        os.remove(launcher)

def create_new():
    shutil.copytree('pycm', module_path)
    shutil.copytree('glade', GLADE_DIR)
    shutil.copytree('img', IMAGE_DIR)

    shutil.copyfile('pycm.py', '/usr/bin/pycm')
    shutil.copyfile('pyconnection-manager.desktop', launcher)

    dir_list = [module_path, GLADE_DIR, IMAGE_DIR]

    for i in dir_list:
        os.chmod(i, 655)

__init__()