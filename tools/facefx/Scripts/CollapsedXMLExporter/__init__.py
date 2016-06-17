""" CollapsedXMLExporter FaceFX Studio Plugin definition.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import PluginManagerUI
import collapsedxmlexporter
import FxStudio

_COLLAPSEDXMLEXPORTER_VERSION = '1.0'
_COLLAPSEDXMLEXPORTER_AUTHOR = 'OC3 Entertainment'
_COLLAPSEDXMLEXPORTER_DESC = 'Exports a collapsed XML actor file.'


def info():
    """ Return the tuple with information about the plugin.

    This is a __facefx__ native plugin, meaning it will default to being
    loaded on a fresh install of FaceFX Studio.

    """
    return (_COLLAPSEDXMLEXPORTER_VERSION, _COLLAPSEDXMLEXPORTER_AUTHOR, _COLLAPSEDXMLEXPORTER_DESC)


def load():
    """ Load the plugin.

    """
    if not FxStudio.isCommandLineMode():
        # Use this code to add one menu item.
        PluginManagerUI.add_export_menu_item(collapsedxmlexporter.MENU_EXPORT_ID,
            'Export Collapsed XML Actor...',
            collapsedxmlexporter.on_menu_export)

        if FxStudio.isNoSave():
            PluginManagerUI.disable_export_menu_item(collapsedxmlexporter.MENU_EXPORT_ID)


def unload():
    """ Unload the plugin.

    """
    if not FxStudio.isCommandLineMode():
        PluginManagerUI.remove_export_menu_item(collapsedxmlexporter.MENU_EXPORT_ID,
            collapsedxmlexporter.on_menu_export)
