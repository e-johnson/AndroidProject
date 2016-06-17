# This script creates an analysis actor that generates curves suitable for body gestures.
# It requires the Rhythm events
# Run the GestureLib.py script first.

from FxStudio import *
from FxGestureShared import *
import copy

# Create the Rhythm event group.
RhythmEventsGroup = "_RhythmEventGroup"
issueCommand('animGroup -create -group "%s";' % (RhythmEventsGroup))

# These are the analysis-generated Rhythm events that are responsible for making the above curves.
# They are guranteed to be at least .4 seconds apart. Meaningful silences (determined by their length
# and how long it's been since another silence) seperate the stresses into Rhythm_Initial, 0 or more
# Rhythm_Middle, then Rhythm_Final.  If the stress stands alone in between silences it is a Rhythm_Isolated.
# First is Rhythm_First, last is Rhythm_Last.
Rhythm_First = "Rhythm_First"
Rhythm_Last = "Rhythm_Last"
Rhythm_Middle = "Rhythm_Middle"
Rhythm_Isolated = "Rhythm_Isolated"
Rhythm_Initial = "Rhythm_Initial"
Rhythm_Final = "Rhythm_Final"


# The output curve names aren't specific to the type of movement that they are mapped to
# because they can be used for different purposes.  The curves are one of three types:
#   1. Bump - a typical 3-key curve with the first and last keys at 0, and the middle key at 1
#   2. Walk - a persistent curve that does a random walk between 0 and 1
#   3. OnOff - a persistent curve that is either 0 or 1 or blending in between
gestureBump = "gestureBump"
gestureOnOff = "gestureOnOff"
gestureBumpWide = "gestureBumpWide"
gestureWalk1 = "gestureWalk1"
gestureWalk2 = "gestureWalk2"
postureShift = "postureShift"
# altPose is essentially an OnOff curve, but it has a special purpose.  It shifts the actor
# from one "phase" to another.  The same curves can have different meanings in the different
# phases.
phasePick1 = "phasePick1"
altPose = "altPose"

activateArmGestures = "activateArmGestures"

# Most of the Rhythm events are simply mapped to these "Important" events where most of the actual
# work is done.
Rhythm_Important_All = "Rhythm_Important_All"
Rhythm_Important_Pick1 = "Rhythm_Important_Pick1"

# Create combiner nodes for the output curves.
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (gestureBump))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (gestureOnOff))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (gestureBumpWide))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (altPose))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (gestureWalk1))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (gestureWalk2))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (postureShift))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s";' % (activateArmGestures))

Rhythm_Important_AllAnim = Anim(Rhythm_Important_All, RhythmEventsGroup)
Rhythm_Important_AllEvent = Event(Rhythm_Important_AllAnim.name, Rhythm_Important_AllAnim.group)


# The animations that create the curves.
gestureBumpAnim = Anim(gestureBump, RhythmEventsGroup)
gestureBumpCurve = Curve(gestureBump)
gestureBumpCurve.keys.append(Key(0, 0))
gestureBumpCurve.keys.append(Key(.3, 1))
gestureBumpCurve.keys.append(Key(.6, 0))
gestureBumpAnim.curves.append(gestureBumpCurve)
gestureBumpAnim.buildAnim()

gestureOnOffPick1 = "gestureOnOffPick1"
gestureOnOffPick1Anim = Anim(gestureOnOffPick1, RhythmEventsGroup)
gestureOnOffAnim = Anim(gestureOnOff, RhythmEventsGroup)
gestureOnOffAnim.curves.append(OneSecondCurve(gestureOnOffAnim.name, 1))
gestureOnOffAnim.buildAnim()
gestureOnOffEvent = Event(gestureOnOffAnim.name, gestureOnOffAnim.group)
gestureOnOffEvent.persist = "true"
gestureOnOffEvent.set_blendin(.5)
gestureOnOffEvent.set_blendout(.5)
gestureOnOffEvent.set_magnitude(1)
gestureOnOffEvent.set_duration(.8)
gestureOnOffEvent.weight = .5
gestureOnOffPick1Anim.events.append(gestureOnOffEvent)
gestureOnOffEvent2 = copy.deepcopy(gestureOnOffEvent)
gestureOnOffEvent2 .weight = 1
gestureOnOffEvent2 .set_magnitude(0)
gestureOnOffPick1Anim.events.append(gestureOnOffEvent2)
gestureOnOffPick1Anim.groupChildEvents = "true"
gestureOnOffPick1Anim.buildAnim()


gestureBumpWideAnim = Anim(gestureBumpWide, RhythmEventsGroup)
gestureBumpWideCurve = Curve(gestureBumpWide)
gestureBumpWideCurve.keys.append(Key(-.6, 0))
gestureBumpWideCurve.keys.append(Key(-.233, 1))
gestureBumpWideCurve.keys.append(Key(.233, 1))
gestureBumpWideCurve.keys.append(Key(.6, 0))
gestureBumpWideAnim.curves.append(gestureBumpWideCurve)
gestureBumpWideAnim.buildAnim()

gestureWalk1Anim = Anim(gestureWalk1, RhythmEventsGroup)
gestureWalk1Anim.curves.append(OneSecondCurve(gestureWalk1Anim.name, 1))
gestureWalk1Anim.buildAnim()

gestureWalk2Anim = Anim(gestureWalk2, RhythmEventsGroup)
gestureWalk2Anim.curves.append(OneSecondCurve(gestureWalk2Anim.name, 1))
gestureWalk2Anim.buildAnim()

postureShiftAnim = Anim(postureShift, RhythmEventsGroup)
postureShiftAnim.curves.append(OneSecondCurve(postureShiftAnim.name, 1))
postureShiftAnim.buildAnim()

altPoseAnim = Anim(altPose, RhythmEventsGroup)
altPoseAnim.curves.append(OneSecondCurve(altPoseAnim.name, 1))
altPoseAnim.buildAnim()
phasePick1Anim = Anim(phasePick1, RhythmEventsGroup)
altPoseEvent = Event(altPoseAnim.name, altPoseAnim.group)
altPoseEvent.set_blendin(.5)
altPoseEvent.set_blendout(.5)
altPoseEvent.minstart = -.2
altPoseEvent.maxstart = -.1
altPoseEvent.minduration = 1
altPoseEvent.maxduration = 1.4
altPoseEvent.inheritmag = "false"
altPoseEvent.inheritdur = "false"
altPoseEvent.persist = "true"
phasePick1Anim.events.append(altPoseEvent)
altPoseEvent2 = copy.deepcopy(altPoseEvent)
altPoseEvent2.set_magnitude(0)
phasePick1Anim.events.append(altPoseEvent2)
phasePick1Anim.groupChildEvents = "true"
phasePick1Anim.buildAnim()


activateArmGesturesAnim = Anim(activateArmGestures, "_AnimEventGroup")
activateArmGesturesAnim.curves.append(OneSecondCurve(activateArmGesturesAnim.name, 1))
activateArmGesturesAnim.buildAnim()

activateArmGesturesEvent = Event(activateArmGesturesAnim.name, activateArmGesturesAnim.group)
activateArmGesturesEvent.blendunscaled = "true"
animEntireAnim = Anim("Anim_Entire", "_AnimEventGroup")
altPoseEvent.set_blendin(.333)
altPoseEvent.set_blendout(.333)
animEntireAnim.events.append(activateArmGesturesEvent)
animEntireAnim.buildAnim()

# Rhythm_Initial setup
# This is probably the most important analysis event.  For one thing, we are garunteed to have
# at least .8 seconds before the last Rhythm_Initial event, because by definiition, a Rhythm_Initial
# must at least be followed by a Rhythm_Final and normally one or more Rhythm_Middle too.  Each of
# these is guranteed to be .4 seconds apart, so we have at least .8 before Rhythm_Initial

postureShiftEvent = Event(postureShiftAnim.name, postureShiftAnim.group)
postureShiftEvent.persist = "true"
postureShiftEvent.set_blendin(.5)
postureShiftEvent.set_blendout(.5)
postureShiftEvent.set_start(-.4)
postureShiftEvent.probability = .4
postureShiftEvent.minmagnitude = 0
postureShiftEvent.maxmagnitude = 1

phasePick1Event = Event(phasePick1Anim.name, phasePick1Anim.group)
phasePick1Event.set_start(-.3)
phasePick1Event.probability = .6
phasePick1Event.inheritmag = "false"
phasePick1Event.inheritdur = "false"

Rhythm_InitialAnim = Anim(Rhythm_Initial, RhythmEventsGroup)
Rhythm_InitialAnim.events.append(Rhythm_Important_AllEvent)
Rhythm_InitialAnim.events.append(postureShiftEvent)
Rhythm_InitialAnim.events.append(phasePick1Event)
Rhythm_InitialAnim.buildAnim()

# Final, Last, and Isolated just fire an "Important" event
Rhythm_FinalAnim = Anim(Rhythm_Final, RhythmEventsGroup)
Rhythm_LastAnim = Anim(Rhythm_Last, RhythmEventsGroup)
Rhythm_IsolatedAnim = Anim(Rhythm_Isolated, RhythmEventsGroup)
Rhythm_FinalAnim.events.append(Rhythm_Important_AllEvent)
Rhythm_LastAnim.events.append(Rhythm_Important_AllEvent)
Rhythm_IsolatedAnim.events.append(Rhythm_Important_AllEvent)
Rhythm_FinalAnim.buildAnim()
Rhythm_LastAnim.buildAnim()
Rhythm_IsolatedAnim.buildAnim()

# The "Important" events that are fired from most Rhythm events
Rhythm_Important_Pick1Anim = Anim(Rhythm_Important_Pick1, RhythmEventsGroup)
Rhythm_Important_Pick1Event = Event(Rhythm_Important_Pick1Anim.name, Rhythm_Important_Pick1Anim.group)

gestureWalk1Event = Event(gestureWalk1Anim.name, gestureWalk1Anim.group)
gestureWalk1Event.set_start(-.333)
gestureWalk1Event.minmagnitude = 0
gestureWalk1Event.maxmagnitude = 1
gestureWalk1Event.set_blendin(.5)
gestureWalk1Event.set_blendout(.5)
gestureWalk1Event.persist = "true"
gestureWalk1Event.inheritmag = "false"
gestureWalk1Event.inheritdur = "false"

gestureWalk2Event = Event(gestureWalk2Anim.name, gestureWalk2Anim.group)
gestureWalk2Event.set_start(-.333)
gestureWalk2Event.minmagnitude = 0
gestureWalk2Event.maxmagnitude = 1
gestureWalk2Event.set_blendin(.5)
gestureWalk2Event.set_blendout(.5)
gestureWalk2Event.persist = "true"
gestureWalk2Event.inheritmag = "false"
gestureWalk2Event.inheritdur = "false"

gestureBumpWideEvent = Event(gestureBumpWideAnim.name, gestureBumpWideAnim.group)
Rhythm_Important_Pick1Anim.groupChildEvents = "true"
Rhythm_Important_Pick1Anim.events.append(gestureBumpWideEvent)
Rhythm_Important_Pick1Anim.events.append(gestureWalk1Event)
Rhythm_Important_Pick1Anim.events.append(gestureWalk2Event)
Rhythm_Important_Pick1Anim.buildAnim()

gestureBumpEvent = Event(gestureBumpAnim.name, gestureBumpAnim.group)
gestureBumpEvent.minduration = 1
gestureBumpEvent.maxduration = 2
gestureBumpEvent.minmagnitude = .5
gestureBumpEvent.maxmagnitude = 1
gestureBumpEvent.set_start(-.3)
gestureBumpEvent.probability = .5
Rhythm_Important_AllAnim.events.append(gestureBumpEvent)
Rhythm_Important_AllAnim.events.append(Rhythm_Important_Pick1Event)
gestureOnOffPick1Event = Event(gestureOnOffPick1Anim.name, gestureOnOffPick1Anim.group)
gestureOnOffPick1Event.set_start(-.3)
gestureOnOffPick1Event.probability = .5
Rhythm_Important_AllAnim.events.append(gestureOnOffPick1Event)
Rhythm_Important_AllAnim.buildAnim()

# Rhythm_Middle
# This is the most frequent Rhythm event, so be careful what goes in here.
Rhythm_MiddleAnim = Anim(Rhythm_Middle, RhythmEventsGroup)
gestureOnOffPick1Event2 = copy.deepcopy(gestureOnOffPick1Event)
gestureOnOffPick1Event2.probability = .1
Rhythm_MiddleAnim.events.append(gestureOnOffPick1Event2)
gestureBumpEvent2 = copy.deepcopy(gestureBumpEvent)
gestureBumpEvent2.probablility = .3
Rhythm_MiddleAnim.events.append(gestureBumpEvent2)
Rhythm_MiddleAnim.buildAnim()
