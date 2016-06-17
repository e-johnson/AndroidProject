"""
A simple GUI for iterating through potential error areas created by the
ConfidenceScoreCompiler.

Owner: Doug Perkowski

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import wx
import FxStudio
from FxAnimation import *
import subprocess

MENU_ID = wx.NewId()

DIALOG_TITLE = "Confidence Analyzer"

STATIC_TEXT_MESSAGE = u'Find text or analysis errors'

# The amount to pad start times (to make sure we see the beginning of the
# problem area)
START_PADDING = .25


def createFrame(commandEvent, errorAreas):
    # Passing in FxStudio.getMainWindowNotebook() as the parent does not prevent
    # a crash on close if the plugin GUI was not closed first.  Instead, we use
    # the appshutdown callback to clean up the plugin.  See the __init__ and
    # __del__ functions.
    frame = ConfidenceScoreGUI(None, errorAreas)
    frame.Show()
    frame.OnRefresh()


[wxID_CONFIDENCEGUI, wxID_CONFIDENCEGUIBUTTON1, wxID_CONFIDENCEGUIBUTTON2, wxID_CONFIDENCEGUIBUTTON3,
 wxID_CONFIDENCEGUIBUTTON4, wxID_CONFIDENCEGUIPANEL1, wxID_FRAME1STATICTEXT1,
] = [wx.NewId() for _init_ctrls in range(7)]


class ConfidenceScoreGUI(wx.Frame):

    def __init__(self, parent, errorAreas):
        self.errorIndex = -1
        self._init_ctrls(parent)
        self.errorAreas = errorAreas
        # Define FxStudio signals here.
        # Clean up the plugin
        FxStudio.connectSignal('appshutdown', self.OnAppShutdown)

    def __del__(self):
        # Clean up FxStudio signals here.
        FxStudio.disconnectSignal('appshutdown', self.OnAppShutdown)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.panel1.SetSizer(self.boxSizer1)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizer2, 0, border=10,  flag=wx.ALL | wx.GROW | wx.EXPAND)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=0, flag=0)
        parent.AddWindow(self.button1, 0, border=0, flag=0)
        parent.AddWindow(self.button2, 0, border=0, flag=0)
        parent.AddWindow(self.button3, 0, border=0, flag=0)
        parent.AddWindow(self.button4, 0, border=0, flag=0)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_CONFIDENCEGUI, name='', parent=prnt,
              size=wx.Size(200, 140),
              style=wx.DEFAULT_FRAME_STYLE, title='Anim Review')
        self.SetClientSize(wx.Size(200, 140))

        self.panel1 = wx.Panel(id=wxID_CONFIDENCEGUIPANEL1, name='panel1', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(200, 140),
              style=wx.SIMPLE_BORDER)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label=STATIC_TEXT_MESSAGE,
              name='staticText1', parent=self.panel1, pos=wx.Point(10, 10),
              size=wx.Size(150, 30), style=0)
        self.staticText1.SetToolTipString(u'staticText1')
        self.staticText1.Show(True)

        self.button1 = wx.Button(id=wxID_CONFIDENCEGUIBUTTON1, label=u'Next Low Confidence',
              name='button1', parent=self.panel1, pos=wx.Point(10, 40),
              size=wx.Size(150, 23), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnNextButtonClicked,
              id=wxID_CONFIDENCEGUIBUTTON1)

        self.button2 = wx.Button(id=wxID_CONFIDENCEGUIBUTTON2, label=u'Play',
              name='button2', parent=self.panel1, pos=wx.Point(10, 63),
              size=wx.Size(150, 23), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnPlayButtonClicked,
              id=wxID_CONFIDENCEGUIBUTTON2)

        self.button3 = wx.Button(id=wxID_CONFIDENCEGUIBUTTON3, label=u'Edit Text',
              name='button3', parent=self.panel1, pos=wx.Point(10, 86),
              size=wx.Size(150, 23), style=0)
        self.button3.Bind(wx.EVT_BUTTON, self.OnEditButtonClicked,
              id=wxID_CONFIDENCEGUIBUTTON3)

        self.button4 = wx.Button(id=wxID_CONFIDENCEGUIBUTTON4, label=u'Reanalyze File',
              name='button4', parent=self.panel1, pos=wx.Point(10, 109),
              size=wx.Size(150, 23), style=0)
        self.button4.Bind(wx.EVT_BUTTON, self.OnReanalyzeButtonClicked,
              id=wxID_CONFIDENCEGUIBUTTON4)

        self._init_sizers()
        self.OnRefresh()

    def OnAppShutdown(self):
        self.Destroy()

    def OnRefresh(self):
        if self.errorIndex >= 0:
            self.button2.Enable(True)
            self.button3.Enable(True)
            self.button4.Enable(True)
            self.staticText1.SetLabel(u'{0} of {1} potential errors'.format(self.errorIndex + 1, len(self.errorAreas)))
        else:
            self.staticText1.SetLabel(STATIC_TEXT_MESSAGE)
            self.button2.Enable(False)
            self.button3.Enable(False)
            self.button4.Enable(False)
        if not FxStudio.hasAnalyzeCommand():
            self.button4.Show(False)

    def OnNextButtonClicked(self, event):
        self.errorIndex += 1
        if self.errorIndex < len(self.errorAreas):
            group = self.errorAreas[self.errorIndex]["group"]
            anim = self.errorAreas[self.errorIndex]["anim"]
            starttime = self.errorAreas[self.errorIndex]["starttime"] - START_PADDING
            endtime = self.errorAreas[self.errorIndex]["endtime"]
            FxStudio.issueCommand('select -type "animgroup" -names "{0}"'.format(group))
            FxStudio.issueCommand('select -type "anim" -names "{0}"'.format(anim))
            FxStudio.issueCommand('currentTime -new "{0}"'.format(starttime))
            FxStudio.setVisibleTimeRange(starttime, endtime)
        else:
            self.errorIndex = -1
        self.OnRefresh()

    def OnPlayButtonClicked(self, event):
        group = self.errorAreas[self.errorIndex]["group"]
        anim = self.errorAreas[self.errorIndex]["anim"]
        starttime = self.errorAreas[self.errorIndex]["starttime"] - START_PADDING
        endtime = self.errorAreas[self.errorIndex]["endtime"]
        if FxStudio.getSelectedAnimGroupName() != group:
            FxStudio.issueCommand('select -type "animgroup" -names "{0}"'.format(group))
        if FxStudio.getSelectedAnimName() != anim:
            FxStudio.issueCommand('select -type "anim" -names "{0}"'.format(anim))
        FxStudio.issueCommand('play -start {0} -end {1}'.format(starttime, endtime))

    def OnEditButtonClicked(self, event):
        currentAnimation = Animation(FxStudio.getSelectedAnimGroupName(),
            FxStudio.getSelectedAnimName())
        audiopath = currentAnimation.absoluteAudioAssetPath
        if audiopath.rfind(".") > 0:
            textpath = audiopath[:audiopath.rfind(".")] + ".txt"
            subprocess.Popen('Notepad {0}'.format(textpath))

    def OnReanalyzeButtonClicked(self, event):
        currentAnimation = Animation(FxStudio.getSelectedAnimGroupName(),
            FxStudio.getSelectedAnimName())
        FxStudio.issueCommand('analyze -audio "{0}" -overwrite'.format(
            currentAnimation.absoluteAudioAssetPath))
