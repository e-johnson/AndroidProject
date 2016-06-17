""" FBXImporter FaceFX Studio Plugin definition.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""
import FxStudio
import PluginManagerUI
import messagehandler
import ui


_FBXIMPORTER_VERSION = '1.1'
_FBXIMPORTER_AUTHOR = 'OC3 Entertainment'
_FBXIMPORTER_DESC = 'Create render assets and basic Face Graph from FBX files.'


def info():
    """ Return the tuple with information about the plugin.

    This is a __facefx__ native plugin, meaning it will default to being
    loaded on a fresh install of FaceFX Studio.

    """
    return (_FBXIMPORTER_VERSION, _FBXIMPORTER_AUTHOR, _FBXIMPORTER_DESC)


def load():
    """ Load the plugin by connecting it to the drop handler of the render
    window.

    """
    FxStudio.connectSignal('messagelogged', messagehandler.on_message_logged)
    FxStudio.connectSignal('filesdroppedonviewport', messagehandler.on_drop)
    FxStudio.connectSignal('idle', messagehandler.on_idle)
    FxStudio.connectSignal('renderassetloadfailed', messagehandler.on_renderassetloadfailed)

    if not FxStudio.isCommandLineMode():
        PluginManagerUI.add_menu_item(ui.MENU_ID, ui.MENU_LABEL, ui.show_options_dialog)


def unload():
    """ Unload the plugin by disconnecting it from the drop handler of the
    render window.

    """
    FxStudio.disconnectSignal('messagelogged', messagehandler.on_message_logged)
    FxStudio.disconnectSignal('filesdroppedonviewport', messagehandler.on_drop)
    FxStudio.disconnectSignal('idle', messagehandler.on_idle)

    if not FxStudio.isCommandLineMode():
        PluginManagerUI.remove_menu_item(ui.MENU_ID, ui.show_options_dialog)
