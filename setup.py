#!/usr/bin/env python

try:
    from gi.repository import Gtk, Gdk, Vte, GLib, Pango, GConf, GdkPixbuf
    import json, os, getpass
    from pycm.pycm_globals import *
except ImportError as e:
    print "Error during importing of necessaries modules.\nError is '%s'" % e

import sys


python_path = "/usr/lib/python2.7/dist-packages/"
uid = os.getuid()


try:
    if uid > 0:
        print "You need to be root to install %s" % FULL_NAME
        sys.exit()

    if not os.path.exists(python_path):
        print "I can't find %s" % python_path
        sys.exit()
    else:
        try:
            os.system('cp -R pycm %s' % python_path)
        except:
            print "Error copyng pycm directory"
            sys.exit()

    if not os.path.exists(IMAGE_DIR):
        try:
            os.makedirs(IMAGE_DIR, mode=655)
            os.system('cp img/*.png %s' % IMAGE_DIR)
        except:
            print "Error copyng images directory"
            sys.exit()
    else:
        try:
            print "Found a previuos installation of %s.\nJust copy necessaries file" % FULL_NAME
            os.system('cp img/*.png %s' % IMAGE_DIR)
        except:
            print "Error copyng images directory"
            sys.exit()

    if not os.path.exists(GLADE_DIR):
        try:
            os.makedirs(GLADE_DIR, mode=655)
            os.system('cp glade/*.glade %s' % GLADE_DIR)
            os.system('cp img/*.png %s' % GLADE_DIR)
        except:
            print "Error copyng glade directory"
            sys.exit()
    else:
        try:
            print "Found a previuos installation of %s.\nJust copy necessaries file" % FULL_NAME
            os.system('cp glade/*.glade %s' % GLADE_DIR)
            os.system('cp img/*.png %s' % GLADE_DIR)
        except:
            print "Error copyng glade directory"
            sys.exit()

    #os.system('ln -s %s%s /usr/share/pyshared/%s' % (python_path, NAME, NAME)) 
    try:
        os.system('cp -f pycm.py /usr/bin/')
        os.system('chmod +x /usr/bin/pycm.py')
        os.system('cp -f pyconnection-manager.desktop /usr/share/applications/')
    except:
        print "Error copyng pycm executable"
        sys.exit()
except:
    print "INSTALLATION ERROR"
    sys.exit()


print "Installation ok"

