
import wx
import FxStudio
from FxHelperLibrary import *

MENU_ID = wx.NewId()

REST_BONE_LABEL = "<Rest Bones>"
DIALOG_TITLE = "Remove Bones"


def createFrame(commandEvent):
    # Passing in FxStudio.getMainWindowNotebook() as the parent does not prevent
    # a crash on close if the plugin GUI was not closed first.  Instead, we use
    # the appshutdown callback to clean up the plugin.  See the __init__ and
    # __del__ functions.
    dlg = removebone(FxStudio.getMainWindow())
    dlg.ShowModal()

[wxID_REMOVEBONEFRAME, wxID_REMOVEBONEFRAMEBUTTON1, wxID_REMOVEBONEFRAMECHOICE1, wxID_REMOVEBONEFRAMELISTBOX1,
 wxID_REMOVEBONEFRAMEPANEL1,
] = [wx.NewId() for _init_ctrls in range(5)]


class removebone(wx.Dialog):

    def __init__(self, parent):
        self._init_ctrls(parent)
        # Define FxStudio signals here.
        FxStudio.connectSignal('appshutdown', self.OnAppShutdown)
        #FxStudio.connectSignal('actorchanged', self.OnActorChanged)

    def __del__(self):
        # Clean up FxStudio signals here.
        FxStudio.disconnectSignal('appshutdown', self.OnAppShutdown)
        #FxStudio.disconnectSignal('actorchanged', self.OnActorChanged)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.panel1.SetSizer(self.boxSizer1)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.choice1, 0, border=5, flag=wx.ALL | wx.GROW)
        parent.AddWindow(self.listBox1, 1, border=5, flag=wx.ALL | wx.GROW)
        parent.AddSizer(self.boxSizer2, 0, border=5, flag=wx.ALL)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button1, 0, border=0, flag=0)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_REMOVEBONEFRAME, name='', parent=prnt,
              pos=wx.Point(470, 279), size=wx.Size(261, 257),
              title=DIALOG_TITLE)
        self.SetClientSize(wx.Size(229, 301))

        self.panel1 = wx.Panel(id=wxID_REMOVEBONEFRAMEPANEL1, name='panel1', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(229, 301),
              style=wx.TAB_TRAVERSAL)

        self.choice1 = wx.Choice(choices=[],
              id=wxID_REMOVEBONEFRAMECHOICE1, name='choice1', parent=self.panel1,
              pos=wx.Point(5, 5), size=wx.Size(219, 21), style=0)
        self.choice1.Bind(wx.EVT_CHOICE, self.OnSelectPose,
              id=wxID_REMOVEBONEFRAMECHOICE1)
        self.listBox1 = wx.ListBox(choices=[], id=wxID_REMOVEBONEFRAMELISTBOX1,
              name='listBox1', parent=self.panel1, pos=wx.Point(5, 36),
              size=wx.Size(219, 227), style=wx.LB_EXTENDED)

        self.button1 = wx.Button(id=wxID_REMOVEBONEFRAMEBUTTON1, label=u'Remove Bone',
              name='button1', parent=self.panel1, pos=wx.Point(5, 273),
              size=wx.Size(75, 23), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnRemoveBone,
              id=wxID_REMOVEBONEFRAMEBUTTON1)
        self._init_sizers()
        self.OnRefresh()

    def OnSelectPose(self, event):
        self.OnRefresh()

    def OnRemoveBone(self, event):
        posename = self.choice1.GetString(self.choice1.GetSelection())
        boneselections = self.listBox1.GetSelections()
        boneposecommand = 'bonepose '
        if posename == REST_BONE_LABEL:
            boneposecommand += '-restpose '
        else:
            boneposecommand += '-name "' + posename + '" '
        boneposecommand += '-removebones "'
        for selindex in boneselections:
            boneposecommand += self.listBox1.GetString(selindex) + "|"
        boneposecommand += '"'
        FxStudio.issueCommand(boneposecommand)
        self.OnRefresh()

    def OnActorChanged(self):
        self.OnRefresh()

    def OnRefresh(self):
        selection = self.choice1.GetString(self.choice1.GetSelection())
        self.choice1.Clear()
        self.listBox1.Clear()
        self.choice1.Append(REST_BONE_LABEL)

        for node in FxStudio.getFaceGraphNodeNames():
            if FxStudio.getFaceGraphNodeProperties(node)[0] == "FxBonePoseNode":
                self.choice1.Append(node)

        if not self.choice1.SetStringSelection(selection):
            self.choice1.SetSelection(0)
        selection = self.choice1.GetString(self.choice1.GetSelection())
        if selection == REST_BONE_LABEL:
            for bone in FxStudio.getBoneNames():
                self.listBox1.Append(bone)
        else:
            for bone in FxStudio.getBonePoseBoneNames(selection):
                self.listBox1.Append(bone)

    def OnAppShutdown(self):
        self.Destroy()
