""" FaceFX Studio update checking system.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import *

import httplib
import urllib
import threading
import xml.dom.minidom
import wx

#-------------------------------------------------------------------------------
# Perform an update check.
#-------------------------------------------------------------------------------

_update_checker = None


def updateCheck_onAppShutdown():
    # If the _update_checker thread is not None, wait for it to finish before
    # allowing shutdown to continue.
    global _update_checker
    if _update_checker is not None:
        _update_checker.disable_gui()
        _update_checker.join()


def updateCheck_done():
    global _update_checker
    if _update_checker is not None:
        _update_checker = None
        # Uninstall our appshutdown signal handler.
        disconnectSignal('appshutdown', updateCheck_onAppShutdown)


def checkForUpdates(is_startup_check):
    global _update_checker
    # Prevent multiple simultaneous update checks.
    if _update_checker is None:
        # Install our appshutdown signal handler.
        connectSignal('appshutdown', updateCheck_onAppShutdown)
        _update_checker = UpdateChecker(getAppName(), getAppVersion(), getAppBuildNumber(), is_startup_check)
        _update_checker.start()


#-------------------------------------------------------------------------------
# Update checking infrastructure.
#-------------------------------------------------------------------------------


class UpdateAvailableDialog(wx.Dialog):
    def __init__(self, update_info, is_startup_check):
        self.update_type = update_info['type']
        self.product = update_info['product']
        self.current_version = update_info['current_version']
        self.update_version = update_info['update_version']
        self.update_url = update_info['info_url']

        title = ''
        bold_text = ''

        if self.update_type == 'update':
            title = 'Update Available'
            bold_text = 'A free update of {0} is available!'.format(self.product)
        else:
            title = 'Upgrade Available'
            bold_text = 'An upgrade of {0} is available for purchase!'.format(self.product)

        wx.Dialog.__init__(self, None, wx.ID_ANY, title, style=wx.CAPTION)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        bmp_and_text_sizer = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.StaticBitmap(self)

        bmp.SetIcon(wx.Icon(getAppIconPath(), wx.BITMAP_TYPE_ICO))

        bmp_and_text_sizer.Add(bmp, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)

        text_sizer = wx.BoxSizer(wx.VERTICAL)

        bold_line = wx.StaticText(self, wx.ID_ANY, bold_text)
        bold_line.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        text_sizer.Add(bold_line, 0, wx.ALL, 5)
        text_sizer.Add(wx.StaticText(self, wx.ID_ANY, '{0} {1} is now available (you have {2}).'.format(self.product, self.update_version, self.current_version)), 0, wx.ALL, 5)

        bmp_and_text_sizer.Add(text_sizer, 0, wx.ALL, 5)

        main_sizer.Add(bmp_and_text_sizer, 0, wx.ALL, 5)

        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if is_startup_check:
            button_sizer.Add(wx.Button(self, 1, 'Skip This Version'), 0, wx.ALL | wx.ALIGN_LEFT, 5)
            self.Bind(wx.EVT_BUTTON, self.on_skip_this_version, id=1)

            button_sizer.AddStretchSpacer()

            # The Remind Me Later button intentionally has the id wx.ID_OK because it does nothing.
            button_sizer.Add(wx.Button(self, wx.ID_OK, 'Remind Me Later'), 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        else:
            button_sizer.AddStretchSpacer()

            button_sizer.Add(wx.Button(self, wx.ID_OK, 'Close'), 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        more_information_button = wx.Button(self, 2, 'More Information...')

        button_sizer.Add(more_information_button, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.Bind(wx.EVT_BUTTON, self.on_more_information, id=2)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 0)

        more_information_button.SetFocus()

        self.SetSizerAndFit(main_sizer)
        self.Layout()
        self.CentreOnScreen()

    def on_skip_this_version(self, event):
        if self.update_type == 'update':
            setConsoleVariable('g_skipupdateversion', self.update_version)
        else:
            setConsoleVariable('g_skipupgradeversion', self.update_version)

        self.EndModal(wx.ID_OK)

    def on_more_information(self, event):
        import webbrowser
        webbrowser.open(self.update_url)
        self.EndModal(wx.ID_OK)


class UpToDateDialog(wx.Dialog):
    def __init__(self, product, current_version):
        wx.Dialog.__init__(self, None, wx.ID_ANY, '', style=wx.CAPTION)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        bmp_and_text_sizer = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.StaticBitmap(self)

        bmp.SetIcon(wx.Icon(getAppIconPath(), wx.BITMAP_TYPE_ICO))

        bmp_and_text_sizer.Add(bmp, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)

        text_sizer = wx.BoxSizer(wx.VERTICAL)

        bold_line = wx.StaticText(self, wx.ID_ANY, 'You\'re up-to-date!')
        bold_line.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        text_sizer.Add(bold_line, 0, wx.ALL, 5)
        text_sizer.Add(wx.StaticText(self, wx.ID_ANY, '{0} {1} is the most recent version available.'.format(product, current_version)), 0, wx.ALL, 5)

        bmp_and_text_sizer.Add(text_sizer, 0, wx.ALL, 5)

        main_sizer.Add(bmp_and_text_sizer, 0, wx.ALL, 5)

        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ok_button = wx.Button(self, wx.ID_OK, 'OK')

        button_sizer.Add(ok_button, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 0)

        ok_button.SetFocus()

        self.SetSizerAndFit(main_sizer)
        self.Layout()
        self.CentreOnScreen()


def DisplayUpdateCheckResults(product, current_version, update_info, upgrade_info, is_startup_check):
    if update_info != None and ((is_startup_check and getConsoleVariable('g_skipupdateversion') != update_info['update_version']) or not is_startup_check):
        dlg = UpdateAvailableDialog(update_info, is_startup_check)
        dlg.ShowModal()
        dlg.Destroy()

    if upgrade_info != None and ((is_startup_check and getConsoleVariable('g_skipupgradeversion') != upgrade_info['update_version']) or not is_startup_check):
        dlg = UpdateAvailableDialog(upgrade_info, is_startup_check)
        dlg.ShowModal()
        dlg.Destroy()

    if update_info == None and upgrade_info == None and is_startup_check == False:
        dlg = UpToDateDialog(product, current_version)
        dlg.ShowModal()
        dlg.Destroy()


def DisplayUpdateCheckError(e, is_startup_check):
    if not is_startup_check:
        error('[Update Check Error]: {0}'.format(e))
        wx.MessageBox('An error was encountered while checking for updates. Please check the error console for details.', 'Error', wx.ICON_EXCLAMATION)


class UpdateChecker(threading.Thread):
    def __init__(self, product_name, product_version, build_number, is_startup_check):
        threading.Thread.__init__(self)
        self.product = product_name
        self.current_version = product_version
        self.build_number = build_number
        self.is_startup_check = is_startup_check
        self.show_gui = True

    def disable_gui(self):
        self.show_gui = False

    def run(self):
        try:
            lsconnection = httplib.HTTPSConnection("license.facefx.com")

            url = "/STATELESS/UPDATES/?name=" + self.product + "&ver=" + self.current_version + "&build=" + self.build_number

            lsconnection.request("GET", urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))

            response = lsconnection.getresponse()

            if response.status != 200:
                if self.show_gui:
                    wx.CallAfter(DisplayUpdateCheckError, 'Request Failed! The response status was: {0}'.format(response.status), self.is_startup_check)

                wx.CallAfter(updateCheck_done)
            else:
                data = response.read()

                xmldoc = xml.dom.minidom.parseString(data)

                response = xmldoc.getElementsByTagName('response')

                status = response[0].attributes['status'].value

                if status != 'success':
                    message = response[0].getElementsByTagName('message')[0].childNodes[0].data

                    if self.show_gui:
                        wx.CallAfter(DisplayUpdateCheckError, 'Request Failed! The server response was: {0}'.format(message), self.is_startup_check)

                    wx.CallAfter(updateCheck_done)
                else:
                    update = response[0].getElementsByTagName('update')

                    update_info = None

                    if len(update[0].childNodes) > 0:
                        update_info = {}
                        update_info['type'] = 'update'
                        update_info['product'] = update[0].getElementsByTagName('product')[0].childNodes[0].data
                        update_info['current_version'] = self.current_version
                        update_info['update_version'] = update[0].getElementsByTagName('version')[0].childNodes[0].data
                        update_info['info_url'] = update[0].getElementsByTagName('info_url')[0].childNodes[0].data

                    upgrade = response[0].getElementsByTagName('upgrade')

                    upgrade_info = None

                    if len(upgrade[0].childNodes) > 0:
                        upgrade_info = {}
                        upgrade_info['type'] = 'upgrade'
                        upgrade_info['product'] = upgrade[0].getElementsByTagName('product')[0].childNodes[0].data
                        upgrade_info['current_version'] = self.current_version
                        upgrade_info['update_version'] = upgrade[0].getElementsByTagName('version')[0].childNodes[0].data
                        upgrade_info['info_url'] = upgrade[0].getElementsByTagName('info_url')[0].childNodes[0].data

                    if self.show_gui:
                        wx.CallAfter(DisplayUpdateCheckResults, self.product, self.current_version, update_info, upgrade_info, self.is_startup_check)

                    wx.CallAfter(updateCheck_done)
        except Exception, e:
            if self.show_gui:
                wx.CallAfter(DisplayUpdateCheckError, 'Request Failed! Exception: {0}'.format(e), self.is_startup_check)

            wx.CallAfter(updateCheck_done)
