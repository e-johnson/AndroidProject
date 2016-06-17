""" User interface for the FBX importer plugin.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os
import time
import wx
import FxStudio

from helper import make_relative_to_clientspec_root
from pluginoptions import PluginOptions


_REMEMBERED_SELECTION = None
_IS_NOTIFICATION_DIALOG_VISIBLE = False


def is_notification_dialog_visible():
    global _IS_NOTIFICATION_DIALOG_VISIBLE
    return _IS_NOTIFICATION_DIALOG_VISIBLE


def show_notification_dialog():
    global _IS_NOTIFICATION_DIALOG_VISIBLE
    _IS_NOTIFICATION_DIALOG_VISIBLE = True
    dlg = FBXImporterNotificationDialog()
    result = dlg.ShowModal()
    _IS_NOTIFICATION_DIALOG_VISIBLE = False
    return result


def show_options_dialog(command_event):
    dlg = FBXImporterOptionsDialog()
    return dlg.ShowModal()


def get_remembered_selection():
    global _REMEMBERED_SELECTION
    return _REMEMBERED_SELECTION


_NOTIFICATION_DIALOG_TITLE = "File modification detected"

_NOTIFICATION_TEXT = "FaceFX has detected that one of your FBX files or your " \
"batch export text file\nhas been modified.\n\nFaceFX can synchronize your actor " \
"with these changes by updating bone\nposes, modifying links to morph target " \
"nodes in your face graph, and\nupdating the FBX@Animations animation group. " \
"These operations are not\nundoable.\n\nWould you like to synchronize your actor?\n"

_REMEMBER_SELECTION_LABEL = "Remember my selection for the rest of this session"

_REMEMBER_SELECTION_CHECKBOX_ID = wx.NewId()
_OPTIONS_BUTTON_ID = wx.NewId()

_OPTIONS_DIALOG_TITLE = "FBX Importer Options"

_BROWSE_FOR_BASE_FBX_BUTTON_ID = wx.NewId()
_BROWSE_FOR_BATCH_EXPORT_TEXT_BUTTON_ID = wx.NewId()

_BASE_FBX_FILE_LABEL = "Base FBX File"
_BATCH_EXPORT_TEXT_FILE_LABEL = "Batch Export Text File"

MENU_ID = wx.NewId()
MENU_LABEL = "FBX Importer Options..."


class FBXImporterNotificationDialog(wx.Dialog):

    def __init__(self):
        wx.Dialog.__init__(self, parent=FxStudio.getMainWindow(),\
            title=_NOTIFICATION_DIALOG_TITLE, size=(-1, 240), style=wx.CAPTION)

        self.vertical_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._NOTIFICATION_TEXT = wx.StaticText(self, label=_NOTIFICATION_TEXT)

        self.vertical_sizer.AddWindow(self._NOTIFICATION_TEXT, 0, border=5,\
            flag=wx.ALL | wx.EXPAND)

        self.remember_selection_checkbox = wx.CheckBox(self,\
            id=_REMEMBER_SELECTION_CHECKBOX_ID, label=_REMEMBER_SELECTION_LABEL)

        self.vertical_sizer.AddWindow(self.remember_selection_checkbox, 0,\
            border=5, flag=wx.ALL | wx.GROW)

        self.static_line = wx.StaticLine(self)

        self.vertical_sizer.AddWindow(self.static_line, 0, border=5,\
            flag=wx.ALL | wx.EXPAND)

        self.horizontal_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.options_button = wx.Button(self, id=_OPTIONS_BUTTON_ID,\
            label='Options')

        self.options_button.Bind(wx.EVT_BUTTON, self.on_options,\
            id=_OPTIONS_BUTTON_ID)

        self.horizontal_sizer.AddWindow(self.options_button, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.horizontal_sizer.AddStretchSpacer()

        self.yes_button = wx.Button(self, id=wx.ID_YES, label='Yes')

        self.yes_button.Bind(wx.EVT_BUTTON, self.on_yes, id=wx.ID_YES)

        self.horizontal_sizer.AddWindow(self.yes_button, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.no_button = wx.Button(self, id=wx.ID_NO, label='No')

        self.no_button.Bind(wx.EVT_BUTTON, self.on_no, id=wx.ID_NO)

        self.horizontal_sizer.AddWindow(self.no_button, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.vertical_sizer.AddWindow(self.horizontal_sizer, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.SetSizer(self.vertical_sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def on_options(self, event):
        # Return wx.ID_CANCEL to signal the calling code that it should display
        # the options dialog.
        self.EndModal(wx.ID_CANCEL)

    def on_yes(self, event):
        global _REMEMBERED_SELECTION

        if self.remember_selection_checkbox.GetValue():
            _REMEMBERED_SELECTION = wx.ID_YES
        else:
            _REMEMBERED_SELECTION = None

        self.EndModal(wx.ID_YES)

    def on_no(self, event):
        global _REMEMBERED_SELECTION

        if self.remember_selection_checkbox.GetValue():
            _REMEMBERED_SELECTION = wx.ID_NO
        else:
            _REMEMBERED_SELECTION = None

        self.EndModal(wx.ID_NO)


class FBXImporterOptionsDialog(wx.Dialog):

    def __init__(self):
        wx.Dialog.__init__(self, parent=FxStudio.getMainWindow(),\
            title=_OPTIONS_DIALOG_TITLE, size=(500, 215), style=wx.CAPTION)

        options = PluginOptions()

        self.vertical_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.static_box = wx.StaticBox(self, label='Options')

        self.static_box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)

        base_fbx_label = wx.StaticText(self, label=_BASE_FBX_FILE_LABEL)

        self.static_box_sizer.AddWindow(base_fbx_label, 0, border=5, flag=wx.ALL)

        self.base_fbx_horizontal_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        initial_fbx_abs_path = ''

        if options.fbx_abs_path is not None:
            initial_fbx_abs_path = options.fbx_abs_path

        self.base_fbx_path = wx.TextCtrl(self, value=initial_fbx_abs_path)

        self.base_fbx_horizontal_sizer.AddWindow(self.base_fbx_path, 1, border=5,\
            flag=wx.ALL | wx.GROW)

        self.base_fbx_browse_button = wx.Button(self, id=_BROWSE_FOR_BASE_FBX_BUTTON_ID, label='Browse...')

        self.base_fbx_browse_button.Bind(wx.EVT_BUTTON, self.on_browse_for_base_fbx,\
            id=_BROWSE_FOR_BASE_FBX_BUTTON_ID)

        self.base_fbx_horizontal_sizer.AddWindow(self.base_fbx_browse_button, 0, border=5,\
            flag=wx.ALL | wx.GROW | wx.ALIGN_RIGHT)

        self.static_box_sizer.AddWindow(self.base_fbx_horizontal_sizer, 0, border=0,\
            flag=wx.ALL | wx.GROW)

        batch_export_text_label = wx.StaticText(self, label=_BATCH_EXPORT_TEXT_FILE_LABEL)

        self.static_box_sizer.AddWindow(batch_export_text_label, 0, border=5, flag=wx.ALL)

        self.batch_export_text_horizontal_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.batch_export_text_path = wx.TextCtrl(self, value=options.betf_abs_path)

        self.batch_export_text_horizontal_sizer.AddWindow(self.batch_export_text_path, 1, border=5,\
            flag=wx.ALL | wx.GROW)

        self.batch_export_text_browse_button = wx.Button(self, id=_BROWSE_FOR_BATCH_EXPORT_TEXT_BUTTON_ID, label='Browse...')

        self.batch_export_text_browse_button.Bind(wx.EVT_BUTTON, self.on_browse_for_batch_export_text,\
            id=_BROWSE_FOR_BATCH_EXPORT_TEXT_BUTTON_ID)

        self.batch_export_text_horizontal_sizer.AddWindow(self.batch_export_text_browse_button, 0, border=5,\
            flag=wx.ALL | wx.ALIGN_RIGHT)

        self.static_box_sizer.AddWindow(self.batch_export_text_horizontal_sizer,\
            0, border=0, flag=wx.ALL | wx.GROW)

        self.vertical_sizer.AddWindow(self.static_box_sizer, 0, border=5, flag=wx.ALL | wx.GROW)

        self.button_horizontal_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.button_horizontal_sizer.AddStretchSpacer()

        self.ok_button = wx.Button(self, id=wx.ID_OK, label='OK')

        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

        self.button_horizontal_sizer.AddWindow(self.ok_button, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.cancel_button = wx.Button(self, id=wx.ID_CANCEL, label='Cancel')

        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel, id=wx.ID_CANCEL)

        self.button_horizontal_sizer.AddWindow(self.cancel_button, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.vertical_sizer.AddWindow(self.button_horizontal_sizer, 0, border=5,\
            flag=wx.ALL | wx.GROW)

        self.SetSizer(self.vertical_sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def on_browse_for_base_fbx(self, event):
        options = PluginOptions()
        initial_fbx_abs_path = ''
        if options.fbx_abs_path is not None:
            initial_fbx_abs_path = os.path.dirname(options.fbx_abs_path)
        base_fbx = FxStudio.displayFileOpenDialog(msg=_BASE_FBX_FILE_LABEL, default_path=initial_fbx_abs_path, wildcard='FBX Files (*.fbx)|*.fbx|All Files (*.*)|*.*', file_must_exist=True)
        if base_fbx is not None:
            self.base_fbx_path.SetValue(base_fbx)

    def on_browse_for_batch_export_text(self, event):
        options = PluginOptions()
        betf = FxStudio.displayFileOpenDialog(msg=_BATCH_EXPORT_TEXT_FILE_LABEL, default_path=os.path.dirname(options.betf_abs_path), wildcard='Batch Export Text Files (*.txt)|*.txt|All Files (*.*)|*.*', file_must_exist=True)
        if betf is not None:
            self.batch_export_text_path.SetValue(betf)

    def on_ok(self, event):
        fbx_abs_path = self.base_fbx_path.GetValue()
        betf_abs_path = self.batch_export_text_path.GetValue()

        if len(fbx_abs_path) > 0:
            if not os.path.exists(fbx_abs_path):
                FxStudio.displayMessageBox("The base FBX file does not exist.", "error")
                return
        else:
            fbx_abs_path = None

        if len(betf_abs_path) > 0:
            if not os.path.exists(betf_abs_path):
                FxStudio.displayMessageBox("The batch export text file does not exist.", "error")
                return

        # Set the options and update the timestamps so that the files will
        # register as changed.
        options = PluginOptions()

        current_time = time.time()

        old_fbx_abs_path = options.fbx_abs_path
        old_betf_abs_path = options.betf_abs_path

        if fbx_abs_path is not None:
            if os.path.abspath(old_fbx_abs_path) != os.path.abspath(fbx_abs_path):
                options.fbx_abs_path = fbx_abs_path
                options.fbx_rel_path = make_relative_to_clientspec_root(fbx_abs_path)
                options.fbx_modification_timestamp = current_time
        else:
            options.fbx_abs_path = None
            options.fbx_rel_path = None

        if os.path.abspath(old_betf_abs_path) != os.path.abspath(betf_abs_path):
            options.betf_abs_path = betf_abs_path
            options.betf_rel_path = make_relative_to_clientspec_root(betf_abs_path)
            options.betf_modification_timestamp = current_time

        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        # Intentionally do nothing but cancel the dialog.
        self.EndModal(wx.ID_CANCEL)
