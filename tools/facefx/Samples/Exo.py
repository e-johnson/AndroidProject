# Use the idle animation as a background for all
def myPostAnalysisSignal(groupName, animName):
  FxStudio.issueCommand('previewanim -animation "idle" -starttime -1 -loop 1')

# Disconnect post analysis and idle animation signal.
def myActorChangedSignal():
  FxStudio.disconnectSignal("postanalysis", myPostAnalysisSignal)
  FxStudio.disconnectSignal("actorchanged", myActorChangedSignal)

FxStudio.connectSignal("postanalysis", myPostAnalysisSignal)
FxStudio.connectSignal("actorchanged", myActorChangedSignal)
