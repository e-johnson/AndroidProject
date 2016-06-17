""" User interface for the plugin manager.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio
import wx
import FxMenu


_WINDOW_TITLE = 'Plugin Manager'
_MANAGER_UI = None
_PLUGIN_MENU = None
_IMPORT_MENU = None
_EXPORT_MENU = None


class _Divider(wx.Window):
    """ A little custom-drawn dividing line. That's it. """

    def __init__(self, parent):
        wx.Window.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, (-1, 2))
        self.SetBackgroundColour('UIFaceColour')
        self.SetForegroundColour('UIFaceColour')
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.colors = FxStudio.getColorPalette()

    def on_paint(self, event):
        width, height = self.GetSizeTuple()

        dc = wx.BufferedPaintDC(self)
        dc.SetPen(wx.Pen(self.colors['UIShadowColour'], 1))
        dc.DrawLine(0, 0, width, 0)
        dc.SetPen(wx.Pen(self.colors['UIHighlightColour'], 1))
        dc.DrawLine(0, 1, width, 1)

    def on_erase_background(self, event):
        pass  # intentionally blank to reduce flicker.


class _PluginManagerUI(wx.Dialog):
    """ The plugin manager dialog. """

    def __init__(self, parent):
        from PluginManager import PLUGIN_MANAGER
        self.plugin_manager = PLUGIN_MANAGER

        wx.Dialog.__init__(self, parent, wx.ID_ANY, _WINDOW_TITLE,
            size=(300, 600))

        self.colors = FxStudio.getColorPalette()
        self.SetBackgroundColour(self.colors['UIFaceColour'])
        self.SetForegroundColour(self.colors['BaseColour8'])

        ib = wx.IconBundle()
        ib.AddIconFromFile(FxStudio.getAppIconPath(), wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)

        self.create_controls()

    def _color_for_state(self, is_loaded):
        return (32, 180, 64) if is_loaded else (200, 64, 32)

    def _color_for_author(self, author_name):
        if 'OC3 Entertainment' in author_name:
            return self.colors['AccentColourVeryLight']
        return self.colors['BaseColour8']

    def _label_for_state(self, is_loaded):
        return 'Unload' if is_loaded else 'Load'

    def _create_labeled_text(self, parent, label, text, color=None):
        st_label = wx.StaticText(parent, -1, label)
        st_label.SetForegroundColour(self.colors['BaseColour6'])
        st_text = wx.StaticText(parent, -1, text)
        if color:
            st_text.SetForegroundColour(color)
        else:
            st_text.SetForegroundColour(self.colors['BaseColour8'])
        st_text.Wrap(220)
        return st_label, st_text

    def create_controls(self):
        self.DestroyChildren()

        # Create the scrolled window.
        scrolled_window = FxStudio.createStyledScrolledWindow(self, wx.ID_ANY)
        scrolled_window.SetBackgroundColour(self.colors['UIFaceColour'])

        # Create the sizer to hold any elements that should be scrolled.
        scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        self.button_map = dict()

        for index, plugin in enumerate(self.plugin_manager.plugins):
            # Create the labeled text fields.
            name_label, name_text = self._create_labeled_text(
                scrolled_window, 'Name:', '{0} {1}'.format(
                    plugin.name, plugin.version),
                self._color_for_state(plugin.loaded))
            author_label, author_text = self._create_labeled_text(
                scrolled_window, 'Author:', plugin.author,
                self._color_for_author(plugin.author))
            desc_label, desc_text = self._create_labeled_text(
                scrolled_window, 'Desc:', plugin.description)

            button_id = wx.NewId()
            load_button = FxStudio.createStyledButton(scrolled_window,
                button_id, self._label_for_state(plugin.loaded))
            self.button_map[button_id] = (plugin, name_text, load_button)
            self.Bind(wx.EVT_BUTTON, self.on_plugin_button, id=button_id)

            # Place the labeled text fields into a flex grid sizer.
            grid_sizer = wx.FlexGridSizer(4, 2)
            grid_sizer.AddGrowableCol(1)
            grid_sizer.Add(name_label, 0, wx.ALL, 2)
            grid_sizer.Add(name_text, 0, wx.ALL, 2)
            grid_sizer.Add(author_label, 0, wx.ALL, 2)
            grid_sizer.Add(author_text, 0, wx.ALL, 2)
            grid_sizer.Add(desc_label, 0, wx.ALL, 2)
            grid_sizer.Add(desc_text, 0, wx.ALL, 2)
            grid_sizer.AddSpacer(0)  # gap the label cell
            grid_sizer.Add(load_button, 0, wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT, 8)

            # Add the grid to the scroll window.
            scrolled_sizer.Add(grid_sizer, 0, wx.GROW, 0)
            scrolled_sizer.AddSpacer(8)
            if index != len(self.plugin_manager.plugins) - 1:
                scrolled_sizer.Add(_Divider(scrolled_window), 0, wx.GROW, 0)
                scrolled_sizer.AddSpacer(5)

        scrolled_window.SetSizer(scrolled_sizer)

        # Create the buttons.
        refresh_id = wx.NewId()
        refresh_button = FxStudio.createStyledButton(self, refresh_id, 'Refresh')
        ok_button = FxStudio.createStyledButton(self, wx.ID_OK, 'Dismiss')

        # Add the buttons and scroll window to the main sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(refresh_button, 0, wx.GROW | wx.ALL, 5)
        main_sizer.Add(_Divider(self), 0, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(scrolled_window, 1, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(_Divider(self), 0, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(ok_button, 0, wx.GROW | wx.ALL, 5)

        # Set the dialog's sizer.
        self.SetSizer(main_sizer)

        # Bind the refresh button event.
        self.Bind(wx.EVT_BUTTON, self.on_refresh_button, id=refresh_id)

    def on_refresh_button(self, event):
        self.plugin_manager.refresh()
        self.Freeze()
        self.create_controls()
        self.Layout()
        self.Thaw()

    def on_plugin_button(self, event):
        plugin, name_text, load_button = self.button_map[event.GetId()]

        if plugin.loaded:
            plugin.unload()
        else:
            plugin.load()

        name_text.SetForegroundColour(self._color_for_state(plugin.loaded))
        name_text.Refresh()
        load_button.SetLabel(self._label_for_state(plugin.loaded))

        self.plugin_manager.save_settings()


class _PluginMenuManager(object):
    """ Holds state pertaining to the plugin menu. """
    def __init__(self):
        self.menu = FxMenu.MenuBarMenu('Plugins')
        self.custom_count = 0
        self.is_shown = False

    def show(self):
        if not self.is_shown:
            self.menu.add_to_menubar()

            plugin_manager_id = wx.NewId()
            self.menu.appendItem(plugin_manager_id, 'Plugin Manager...')

            self.menu.bind(self.on_plugin_manager, plugin_manager_id)
            self.is_shown = True

    def add_item(self, item_id, item_name, callback):
        if not self.custom_count:
            self.menu.appendSeparator()

        self.menu.appendItem(item_id, item_name)
        self.menu.bind(callback, item_id)
        self.custom_count += 1

    def add_submenu(self, item_id, item_name, submenu):
        if not self.custom_count:
            self.menu.appendSeparator()

        self.menu.appendSubmenu(item_id, item_name, submenu)
        self.custom_count += 1

    def remove_item(self, item_id, callback):
        self.menu.unbind(callback, item_id)
        self.menu.removeItemById(item_id)
        self.custom_count -= 1

        if not self.custom_count:
            self.menu.removeSeparator()

    def enable_item(self, item_id):
        self.menu.enableItem(item_id, True)

    def disable_item(self, item_id):
        self.menu.enableItem(item_id, False)

    def hide(self):
        if self.is_shown:
            self.menu.remove_from_menubar()

    def on_plugin_manager(self, event):
        global _MANAGER_UI
        if not _MANAGER_UI:
            _MANAGER_UI = _PluginManagerUI(FxStudio.getMainWindow())
        _MANAGER_UI.ShowModal()


def _ensure_created():
    global _PLUGIN_MENU
    if not _PLUGIN_MENU:
        _PLUGIN_MENU = _PluginMenuManager()
    _PLUGIN_MENU.show()


def show():
    """ Show the plugin menu. """
    _ensure_created()


def add_menu_item(item_id, item_name, callback):
    """ Adds a menu item to the Plugins menu.

    The item will execute the callback when clicked.

    """
    _ensure_created()
    global _PLUGIN_MENU
    if _PLUGIN_MENU:
        _PLUGIN_MENU.add_item(item_id, item_name, callback)


def add_submenu(item_id, item_name, submenu):
    _ensure_created()
    global _PLUGIN_MENU
    if _PLUGIN_MENU:
        _PLUGIN_MENU.add_submenu(item_id, item_name, submenu)


def remove_menu_item(item_id, callback):
    _ensure_created()
    global _PLUGIN_MENU
    if _PLUGIN_MENU:
        _PLUGIN_MENU.remove_item(item_id, callback)


def enable_menu_item(item_id):
    _ensure_created()
    global _PLUGIN_MENU
    if _PLUGIN_MENU:
        _PLUGIN_MENU.enable_item(item_id)


def disable_menu_item(item_id):
    _ensure_created()
    global _PLUGIN_MENU
    if _PLUGIN_MENU:
        _PLUGIN_MENU.disable_item(item_id)


def hide():
    """ Hide the plugin menu. """
    global _PLUGIN_MENU
    _PLUGIN_MENU.hide()


def _get_import_menu():
    global _IMPORT_MENU
    if not _IMPORT_MENU:
        _IMPORT_MENU = FxMenu.NativeMenu(FxStudio.getImportMenu())


def add_import_menu_item(item_id, item_name, callback):
    """ Adds a menu item to the File -> Import menu.

    The item will execute the callback when clicked.

    """
    _get_import_menu()
    global _IMPORT_MENU
    if _IMPORT_MENU:
        _IMPORT_MENU.appendItem(item_id, item_name)
        _IMPORT_MENU.bind(callback, item_id)


def remove_import_menu_item(item_id, callback):
    """ Removes a menu item from the File -> Import menu. """
    _get_import_menu()
    global _IMPORT_MENU
    if _IMPORT_MENU:
        _IMPORT_MENU.unbind(callback, item_id)
        _IMPORT_MENU.removeItemById(item_id)


def enable_import_menu_item(item_id):
    """ Enables a menu item in the File -> Import menu. """
    _get_import_menu()
    global _IMPORT_MENU
    if _IMPORT_MENU:
        _IMPORT_MENU.enableItem(item_id, True)


def disable_import_menu_item(item_id):
    """ Disables a menu item in the File -> Import menu. """
    _get_import_menu()
    global _IMPORT_MENU
    if _IMPORT_MENU:
        _IMPORT_MENU.enableItem(item_id, False)


def _get_export_menu():
    global _EXPORT_MENU
    if not _EXPORT_MENU:
        _EXPORT_MENU = FxMenu.NativeMenu(FxStudio.getExportMenu())


def add_export_menu_item(item_id, item_name, callback):
    """ Adds a menu item to the File -> Export menu.

    The item will execute the callback when clicked.

    """
    _get_export_menu()
    global _EXPORT_MENU
    if _EXPORT_MENU:
        _EXPORT_MENU.appendItem(item_id, item_name)
        _EXPORT_MENU.bind(callback, item_id)


def remove_export_menu_item(item_id, callback):
    """ Removes a menu item from the File -> Export menu. """
    _get_export_menu()
    global _EXPORT_MENU
    if _EXPORT_MENU:
        _EXPORT_MENU.unbind(callback, item_id)
        _EXPORT_MENU.removeItemById(item_id)


def enable_export_menu_item(item_id):
    """ Enables a menu item in the File -> Export menu. """
    _get_export_menu()
    global _EXPORT_MENU
    if _EXPORT_MENU:
        _EXPORT_MENU.enableItem(item_id, True)


def disable_export_menu_item(item_id):
    """ Disables a menu item in the File -> Export menu. """
    _get_export_menu()
    global _EXPORT_MENU
    if _EXPORT_MENU:
        _EXPORT_MENU.enableItem(item_id, False)
