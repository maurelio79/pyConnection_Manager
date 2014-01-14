# -*- coding: utf-8; -*-

import os, getpass


__all__ = [
    'NAME', 'VERSION', 'IMAGE_DIR', 'GLADE_DIR', 'LOCALE_DIR', 'GCONF_PATH', 'KEY', 'DB_PATH',
    'HOSTNAME', 'USERNAME', 'TERMINAL_MATCH_EXPRS', 'TERMINAL_MATCH_TAGS', 'FULL_NAME',
    'SHELLS_FILE', 'USER_SHELL_VALUE', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_LEFT',
    ]

NAME = 'pycm'
FULL_NAME = 'pyConnection Manager'
VERSION = '0.1.1'
IMAGE_DIR = '/usr/share/pixmaps/' + NAME
GLADE_DIR = '/usr/share/' + NAME
LOCALE_DIR = '/usr/share/locale'

HOSTNAME = os.uname()[1]
USERNAME = getpass.getuser()

# Gconf stuff. Yep, it is hardcoded =)
GCONF_PATH = '/apps/pycm'
KEY = lambda x: (GCONF_PATH+x)

# DB server stuff
DB_PATH = '/home/' + USERNAME + '/.' + NAME

# Default user shell
#USER_SHELL_VALUE = _('<user shell>')
USER_SHELL_VALUE = '/bin/bash'
# Shell file to load possible shell
SHELLS_FILE = '/etc/shells'

# regular expressions to highlight links in terminal. This code was
# lovely stolen from the great gnome-terminal project, thank you =)
USERCHARS = "-[:alnum:]"
PASSCHARS = "-[:alnum:],?;.:/!%$^*&~\"#'"
HOSTCHARS = "-[:alnum:]"
HOST      = "[" + HOSTCHARS + "]+(\\.[" + HOSTCHARS + "]+)*"
PORT      = "(:[:digit:]{1,5})?"
PATHCHARS =  "-[:alnum:]_$.+!*(),;:@&=?/~#%"
SCHEME    = "(news:|telnet:|nntp:|file:/|https?:|ftps?:|webcal:)"
USER      = "[" + USERCHARS + "]+(:[" + PASSCHARS + "]+)?"
URLPATH   = "/[" + PATHCHARS + "]*[^]'.}>) \t\r\n,\\\"]"

TERMINAL_MATCH_EXPRS = [
  "\<" + SCHEME + "//(" + USER + "@)?" + HOST + PORT + "(" + URLPATH + ")?\>/?",
  "\<(www|ftp)[" + HOSTCHARS + "]*\." + HOST + PORT + "(" +URLPATH + ")?\>/?",
  "\<(mailto:)?[" + USERCHARS + "][" + USERCHARS + ".]*@[" + HOSTCHARS +
  "]+\." + HOST + "\>"
  ]

TERMINAL_MATCH_TAGS = 'schema', 'http', 'email'
ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT = range(3)