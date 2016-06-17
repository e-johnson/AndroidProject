""" FaceFX Studio menu system.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import getMainWindow
from FxStudio import _new_Menu
from FxStudio import _delete_Menu
from FxStudio import _Menu_appendItem
from FxStudio import _Menu_appendSubmenu
from FxStudio import _Menu_appendSeparator
from FxStudio import _Menu_removeItemById
from FxStudio import _Menu_removeItemByCaption
from FxStudio import _Menu_removeSeparator
from FxStudio import _Menu_enableItem
from FxStudio import _Menu_checkItem
from FxStudio import _addMenuToMenuBar
from FxStudio import _removeMenuFromMenuBar

import wx


# Defines a menu in FaceFX Studio. Menus can be added as submenu items to other
# menus, or docked into the main menu bar in FaceFX Studio via MenuBarMenu.
class Menu:

    def __init__(self):
        self._menu = None
        self._ownsmenu = False
        self.bindings = []

    def acquire(self):
        self._menu = _new_Menu()
        self._ownsmenu = True

    def release(self):
        # This iterates through a *copy* of self.bindings since we will be
        # removing items in a loop.
        for binding in self.bindings[:]:
            self.unbind(binding[0], binding[1])
        if self._ownsmenu:
            _delete_Menu(self._menu)
        self._menu = None

    def appendItem(self, id, caption, enabled_icon_path='', disabled_icon_path='', enabled_icon=None, disabled_icon=None):
        # Pass the icon objects if both are non-None.
        if enabled_icon is not None and disabled_icon is not None:
            _Menu_appendItem(self._menu, id, caption, enabled_icon=enabled_icon, disabled_icon=disabled_icon)
        else:
            # If both icons are None, fall back on the icon paths.
            if enabled_icon is None and disabled_icon is None:
                # Pass in the icon paths if both are non-default.
                if enabled_icon_path is not '' and disabled_icon_path is not '':
                    _Menu_appendItem(self._menu, id, caption, enabled_icon_path, disabled_icon_path)
                else:
                    # If both icon paths are default, don't pass them.
                    if enabled_icon_path is '' and disabled_icon_path is '':
                        _Menu_appendItem(self._menu, id, caption)
                    else:
                        # Otherwise one is default and the other is not, so let that case trigger the
                        # exception inside _Menu_appendItem to display the appropriate error message
                        # to the user.
                        _Menu_appendItem(self._menu, id, caption, enabled_icon_path)
            else:
                # Otherwise one is None and the other is not, so let that case trigger the
                # exception inside _Menu_appendItem to display the appropriate error message
                # to the user.
                _Menu_appendItem(self._menu, id, caption, enabled_icon=enabled_icon)

    def appendSubmenu(self, id, caption, submenu):
        _Menu_appendSubmenu(self._menu, id, caption, submenu._menu)
        submenu._ownsmenu = False

    def appendSeparator(self):
        _Menu_appendSeparator(self._menu)

    def removeItemById(self, id):
        _Menu_removeItemById(self._menu, id)

    def removeItemByCaption(self, caption):
        _Menu_removeItemByCaption(self._menu, caption)

    def removeSeparator(self):
        _Menu_removeSeparator(self._menu)

    def enableItem(self, id, enabled):
        _Menu_enableItem(self._menu, id, enabled)

    def checkItem(self, id, checked):
        _Menu_checkItem(self._menu, id, checked)

    def bind(self, handler, id):
        # Don't allow duplicate bindings.
        if 0 == self.bindings.count((handler, id)):
            getMainWindow().Bind(wx.EVT_MENU, handler=handler, id=id)
            self.bindings.append((handler, id))

    def unbind(self, handler, id):
        # Since we don't allow duplicate bindings, make sure there are none
        # before unbinding.
        if 1 == self.bindings.count((handler, id)):
            getMainWindow().Unbind(wx.EVT_MENU, handler=handler, id=id)
            self.bindings.remove((handler, id))


# Special type of menu that wraps a FaceFX Studio "native" menu.
class NativeMenu(Menu):

    def __init__(self, native_menu):
        Menu.__init__(self)
        self._menu = native_menu
        self._ownsmenu = False
        self._non_native_ids = []
        self._non_native_separator_count = 0

    def _is_non_native_id(self, id):
        # Is id is in the self._non_native_ids list?
        if len([i for i in self._non_native_ids if i == id]) > 0:
            return True
        else:
            return False

    def acquire(self):
        pass

    def appendItem(self, id, caption, enabled_icon_path='', disabled_icon_path='', enabled_icon=None, disabled_icon=None):
        Menu.appendItem(self, id, caption, enabled_icon_path, disabled_icon_path, enabled_icon, disabled_icon)
        self._non_native_ids.append(id)

    def appendSubmenu(self, id, caption, submenu):
        Menu.appendSubmenu(self, id, caption, submenu)
        self._non_native_ids.append(id)

    def appendSeparator(self):
        Menu.appendSeparator(self)
        self._non_native_separator_count += 1

    def removeItemById(self, id):
        if self._is_non_native_id(id):
            Menu.removeItemById(self, id)
        else:
            raise RuntimeError('{0} is not a valid non-native id in NativeMenu.removeItemById'.format(str(id)))

    def removeItemByCaption(self, caption):
        raise RuntimeError('NativeMenu.removeItemByCaption is not a supported operation')

    def removeSeparator(self):
        if self._non_native_separator_count > 0:
            Menu.removeSeparator(self)
            self._non_native_separator_count -= 1
        else:
            raise RuntimeError('No more non-native separators to remove in NativeMenu.removeSeparator')

    def enableItem(self, id, enabled):
        if self._is_non_native_id(id):
            Menu.enableItem(self, id, enabled)
        else:
            raise RuntimeError('{0} is not a valid non-native id in NativeMenu.enableItem'.format(str(id)))

    def checkItem(self, id, checked):
        if self._is_non_native_id(id):
            Menu.checkItem(self, id, checked)
        else:
            raise RuntimeError('{0} is not a valid non-native id in NativeMenu.checkItem'.format(str(id)))

    def bind(self, handler, id):
        if self._is_non_native_id(id):
            Menu.bind(self, handler, id)
        else:
            raise RuntimeError('{0} is not a valid non-native id in NativeMenu.bind'.format(str(id)))

    def unbind(self, handler, id):
        if self._is_non_native_id(id):
            Menu.unbind(self, handler, id)
        else:
            raise RuntimeError('{0} is not a valid non-native id in NativeMenu.unbind'.format(str(id)))


# Special type of menu that is docked in the main menu bar of FaceFX Studio.
class MenuBarMenu(Menu):

    def __init__(self, caption):
        Menu.__init__(self)
        self.caption = caption

    def add_to_menubar(self):
        Menu.acquire(self)
        _addMenuToMenuBar(self._menu, self.caption)

    def remove_from_menubar(self):
        _removeMenuFromMenuBar(self.caption)
        Menu.release(self)
