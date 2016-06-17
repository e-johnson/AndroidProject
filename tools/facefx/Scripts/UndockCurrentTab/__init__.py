# This script will undock the current tab from the main notebook in Studio and put it in a container frame.
# Holding shift while undocking will cause the floating window to be always-on-top.
# When the container frame is closed, the tab is re-docked back into the main notebook in Studio.

import wx
from FxStudio import *
import PluginManagerUI


_UNDOCK_CURRENT_TAB_VERSION = '1.0'
_UNDOCK_CURRENT_TAB_AUTHOR = 'OC3 Entertainment'
_UNDOCK_CURRENT_TAB_DESC = 'Undocks the currently selected FaceFX Studio tab and places it in a floating window.'

_UNDOCK_CURRENT_TAB_MENUNAME = 'Undock Current Tab'

_MENU_ID = wx.NewId()


def info():
    """ Return the tuple with information about the plugin.

    This is a __facefx__ native plugin, meaning it will default to being
    loaded on a fresh install of FaceFX Studio.

    """
    return (_UNDOCK_CURRENT_TAB_VERSION, _UNDOCK_CURRENT_TAB_AUTHOR, _UNDOCK_CURRENT_TAB_DESC)


def load():
    """ Loads the plugin. """
    if not isCommandLineMode():
        PluginManagerUI.add_menu_item(_MENU_ID, _UNDOCK_CURRENT_TAB_MENUNAME, undock)


def unload():
    """ Unloads the plugin. """
    if not isCommandLineMode():
        PluginManagerUI.remove_menu_item(_MENU_ID, undock)


def undock(commandEvent=wx.CommandEvent()):
    """ Undocks the currently selected FaceFX Studio tab and places it in a floating window. Hold shift while undocking
    to force the floating window to be always-on-top. Closing the window will re-dock the tab.
    """
    try:
        current_tab = getSelectedTabInMainWindowNotebook()
        StudioContainer(getTabWindowInMainWindowNotebook(current_tab), current_tab).SendSizeEvent()
    except RuntimeError:
        # If there are no tabs in the notebook, simply do nothing.
        pass


class StudioContainer(wx.Frame):
    def __init__(self, containee, title):

        frame_style = wx.DEFAULT_FRAME_STYLE

        if wx.GetKeyState(wx.WXK_SHIFT):
            frame_style = frame_style | wx.FRAME_FLOAT_ON_PARENT

        wx.Frame.__init__(self, getMainWindow(), wx.ID_ANY, title, wx.DefaultPosition, (640, 480), style=frame_style)

        # This is how to give a frame our Studio icon.
        ib = wx.IconBundle()
        ib.AddIconFromFile(getAppIconPath(), wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)

        self.containee = containee
        self.containee_title = title

        # Use some Studio theme colors.
        self.color_palette = getColorPalette()
        self.SetBackgroundColour(self.color_palette['BaseColour1'])
        self.SetForegroundColour(self.color_palette['BaseColour8'])

        self.Bind(wx.EVT_CLOSE, self.on_close)

        undockFromMainWindowNotebook(self.containee)
        self.containee.Reparent(self)

        # This is important! What is actually passed to connectSignal() and
        # disconnectSignal() is a method object. Each time you say self.on_app_shutdown
        # Python creates a *new* method object. In order for the connect to match up
        # with the disconnect, we need to make sure that we pass both the *same* method
        # object. Therefore we need to create only one for this instance and keep track
        # of it.
        self.appshutdown_signal_connection = self.on_app_shutdown

        connectSignal('appshutdown', self.appshutdown_signal_connection)

        self.Show(True)
        # This is required for some strange reason I'm not sure about right now. It seems that
        # when undocking / reparenting wxWidgets decides to hide the underlying window even though
        # it doesn't do that in the AudioInterface.py case.
        self.containee.Show(True)

    def __del__(self):
        disconnectSignal('appshutdown', self.appshutdown_signal_connection)

    # Closing the frame manually redocks into the notebook and destroys the frame.
    def on_close(self, event):
        self.containee.Reparent(getMainWindowNotebook())

        dockInMainWindowNotebook(self.containee, self.containee_title, select=True)

        disconnectSignal('appshutdown', self.appshutdown_signal_connection)

        self.Destroy()

    def on_app_shutdown(self):
        disconnectSignal('appshutdown', self.appshutdown_signal_connection)

        self.Destroy()
