""" REMOVEBONES FaceFX Studio Plugin definition.

Owner: Doug Perkowski

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import removebones
import PluginManagerUI
import FxStudio

_REMOVEBONES_MENUNAME = "Remove Bones..."

_REMOVEBONES_VERSION = '1.0'
_REMOVEBONES_AUTHOR = 'OC3 Entertainment'
_REMOVEBONES_DESC = 'Remove bones from bone poses or rest bones.'


def info():
    """ Return the tuple with information about the plugin.

    """
    return (_REMOVEBONES_VERSION, _REMOVEBONES_AUTHOR, _REMOVEBONES_DESC)


def load():
    """ Load the plugin
    """
    if not FxStudio.isCommandLineMode():
        PluginManagerUI.add_menu_item(removebones.MENU_ID, _REMOVEBONES_MENUNAME, removebones.createFrame)


def unload():
    """ Unload the plugin

    """
    if not FxStudio.isCommandLineMode():
        PluginManagerUI.remove_menu_item(removebones.MENU_ID, removebones.createFrame)
