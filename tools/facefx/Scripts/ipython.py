# This script pops up an interactive IPython shell configured for use in
# FaceFX Studio and configures Studio's Python environment.

import wx
import sys
import string
from IPython.gui.wx.ipython_view import IPShellWidget
import IPython.ipapi
import FxStudio


class CodeGenerator:

    def __init__(self):
        self.begin()

    def begin(self):
        self.code = []
        self.tab = "    "
        self.level = 0

    def getCode(self):
        return string.join(self.code, "")

    def write(self, string):
        self.code.append(self.tab * self.level + string)

    def indent(self):
        self.level = self.level + 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError('tab level is already 0!')
        self.level = self.level - 1

    def compile(self):
        bytecode = compile(self.getCode(), '<string>', 'exec')
        ip = IPython.ipapi.get()
        ip.ev(bytecode)


def wrap_studio_command_with_magic(cmd, docstr):
    cg = CodeGenerator()
    cg.begin()
    cg.write("import FxStudio\n")
    cg.write("import IPython.ipapi\n")
    cg.write("ip = IPython.ipapi.get()\n")
    cg.write("\n")
    cg.write("def facefx_magic_wrap_")
    cg.write(cmd)
    cg.write("(self, arg):\n")
    cg.indent()
    cg.write("\"\"\"\n")
    cg.write(docstr)
    cg.write("\n\"\"\"\n")
    cg.write("FxStudio.issueCommand(\"")
    cg.write(cmd)
    cg.write(" %s\" % arg.replace(\'\\\'\', \'\\\"\'))\n")
    cg.dedent()
    cg.write("\n")
    cg.write("ip.expose_magic('")
    cg.write(cmd)
    cg.write("', facefx_magic_wrap_")
    cg.write(cmd)
    cg.write(")\n")
    cg.compile()


def magicfy_all_studio_commands():
    cmd_list = FxStudio.getConsoleCommandList()
    for cmd in cmd_list:
        if cmd != 'quit' and cmd != 'exit':
            wrap_studio_command_with_magic(cmd, FxStudio.getConsoleCommandHelp(cmd))


class FaceFXOnDemandOutputWindow:

    def __init__(self, title="wxPython: stdout/stderr"):
        self.frame = None
        self.title = title
        self.pos = wx.DefaultPosition
        self.size = (800, 600)
        self.color_palette = FxStudio.getColorPalette()
        self.triggers = []
        self.logfile = open(FxStudio.getDirectory('logs') + FxStudio.getConsoleVariable('g_applaunchtime') + "-python-log.txt", "w")
        self.continue_line = False

    def __del__(self):
        self.logfile.close()

    def raiseWhenSeen(self, trigger):
        import types
        if type(trigger) in types.StringTypes:
            trigger = [trigger]
        self.triggers = trigger

    def createOutputWindow(self, st):
        if FxStudio.getConsoleVariableAsSwitch('py_enableoutputwindow') == True:
            self.frame = wx.Frame(FxStudio.getMainWindow(), -1, self.title, self.pos, self.size,
                                  style=wx.DEFAULT_FRAME_STYLE)
            self.text = wx.TextCtrl(self.frame, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
            self.text.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, FxStudio.getUnicodeFontName(), wx.FONTENCODING_SYSTEM))
            self.text.SetBackgroundColour(self.color_palette['BaseColour1'])
            self.text.SetForegroundColour(self.color_palette['BaseColour8'])
            ib = wx.IconBundle()
            ib.AddIconFromFile(FxStudio.getAppIconPath(), wx.BITMAP_TYPE_ANY)
            self.frame.SetIcons(ib)
            self.text.AppendText(st)
            self.log_to_file(st)
            self.frame.Show(True)
            self.frame.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        else:
            self.log_to_file(st)

    def onCloseWindow(self, event):
        if self.frame is not None:
            self.frame.Destroy()
        self.frame = None
        self.text = None

    def log_to_file(self, text):
        import time as __facefx_time
        if not text.isspace() and not self.continue_line:
            logtext = __facefx_time.strftime("%H:%M:%S", __facefx_time.localtime()) + ": " + text
            self.logfile.write(logtext)
        elif text.isspace() and not self.continue_line:
            logtext = __facefx_time.strftime("%H:%M:%S", __facefx_time.localtime()) + ": " + text
            self.logfile.write(logtext)
        else:
            self.logfile.write(text)
        self.logfile.flush()
        if text.endswith(('\n', '\r')):
            self.continue_line = False
        else:
            self.continue_line = True

    def write(self, text):
        if self.frame is None:
            if not wx.Thread_IsMain():
                wx.CallAfter(self.CreateOutputWindow, text)
            else:
                self.createOutputWindow(text)
        else:
            if not wx.Thread_IsMain():
                wx.CallAfter(self.__write, text)
            else:
                self.__write(text)

    def __write(self, text):
        self.text.AppendText(text)
        self.log_to_file(text)
        for item in self.triggers:
            if item in text:
                self.frame.Raise()
                break

    def close(self):
        if self.frame is not None:
            wx.CallAfter(self.frame.Close)

    def flush(self):
        pass


class FaceFXIPythonShell(wx.Window):

        def __init__(self, parent, id, title):
            wx.Window.__init__(self, parent, id, style=wx.NO_BORDER, name=title)
            self._sizer = wx.BoxSizer(wx.VERTICAL)
            self.shell = IPShellWidget(self, intro='Welcome to the FaceFX IPython Shell.\n\n')
            # Turn on STC completion and turn off threading.
            self.shell.options['completion']['value'] = 'STC'
            self.shell.options['threading']['value'] = 'False'
            self.shell.reloadOptions(self.shell.options)
            # Turn off the annoying 80 column vertical line.
            self.shell.text_ctrl.SetEdgeMode(wx.stc.STC_EDGE_NONE)
            self.color_palette = FxStudio.getColorPalette()
            self.shell.text_ctrl.StyleSetBackground(wx.stc.STC_STYLE_DEFAULT, self.color_palette['BaseColour1'])
            for style in self.shell.text_ctrl.ANSI_STYLES.values():
                self.shell.text_ctrl.StyleSetBackground(style[0], self.color_palette['BaseColour1'])
            self.shell.text_ctrl.SetCaretForeground('WHITE')
            self.shell.text_ctrl.SetWindowStyle(self.shell.text_ctrl.GetWindowStyle() | wx.NO_BORDER)
            self.shell.text_ctrl.Refresh()
            ip = IPython.ipapi.get()
            ip.ex('from FxStudio import *')
            self._sizer.Add(self.shell, 1, wx.EXPAND)
            self.SetSizer(self._sizer)
            self.Bind(wx.EVT_SIZE, self.onSize)
            # Hook into the underlying STC and add in the missing mouse capture lost event handler
            # to prevent C++ wxWidgets code from asserting. Note that there's not much we can
            # do about the selection weirdness that happens if this state is triggered.
            self.shell.text_ctrl.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.onMouseCaptureLost)
            self.SetAutoLayout(1)
            self.output = FaceFXOnDemandOutputWindow(title="output")
            sys.stdout = self.output
            sys.stderr = self.output
            FxStudio.dockInMainWindowNotebook(self, "Python")

        def onSize(self, newSize):
            self.Layout()

        # Do nothing when mouse capture is lost. This causes selection to be a little
        # weird if this happens but will not lock or crash the application or cause the
        # C++ wxWidgets code to assert.
        def onMouseCaptureLost(self, event):
            pass


old = wx.FindWindowByName('FaceFX IPython Shell')
if old == None:
    FxStudio.msg('Starting FaceFX IPython Shell...')
    FxStudio.msg('Using IPython version {0}.'.format(IPython.__version__))
    FxStudio.msg('Using wxPython version {0}.'.format(wx.__version__))
    panel = FaceFXIPythonShell(FxStudio.getMainWindowNotebook(), wx.ID_ANY, 'FaceFX IPython Shell')
    ip = IPython.ipapi.get()
    ip.ex('import ipython')
    ip.ex('ipython.magicfy_all_studio_commands()')
    ipython_log_filename = FxStudio.getDirectory('logs')
    ipython_log_filename += FxStudio.getConsoleVariable('g_applaunchtime')
    ipython_log_filename += '-ipython-log.txt'
    ip.IP.magic_logstart('-o -r -t "{0}"'.format(ipython_log_filename))
    ip.IP.magic_cd(FxStudio.getDirectory('app'))
