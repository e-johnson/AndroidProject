# -----------------------------------------------------------------------------
# This script gets called from Slade.fxl, which in turn is called when
# the Slade.facefx file is opened.
# -----------------------------------------------------------------------------

from FxStudio import getConsoleVariable, issueCommand

# Mount the ExampleGame external animation set, but only do this in FaeFX
# Studio Unlimited because Studio Free and Studio Professional do not support
# mounting and unmounting external animation sets.
if getConsoleVariable('g_productname') == 'FaceFX Studio Unlimited':
    issueCommand('animSet -mount "./Samples/ExampleGame.animset"')
else:
    msg('Slade.py: the current Studio version is not FaceFX Studio Unlimited, skipping animation set mount')
