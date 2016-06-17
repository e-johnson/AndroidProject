#-------------------------------------------------------------------------------
# Create an analysis actor for generating events.
#
#
# Owner: Doug Perkowski
#
# Copyright (c) 2002-2012 OC3 Entertainment, Inc.
#-------------------------------------------------------------------------------
from FxStudio import *
from FxGestureShared import *

# The equals operator doesn't actually copy objects unless you use x = copy.deepcopy(y)
import copy

# An overall parameter to increase or decrease the speed of emphasis gestures
gcSpeed = 1.0
# An overall parameter to increase or decrease the intensity of emphasis gestures
gcMagnitude = 1.0

# In version 1.7, Emphasis and Orientation curves are spit out, and Eye output
# does not contain counter-movement for head rotations.  It requires setup in the
# in-game actor, as opposed to putting that setup (and overhead) into the analysis
# actor where it won't impact performance or cause headaches when setting up.
version_17X_Compatible = getScriptSetting("gesturelib_version_17X_Compatible", "false")

# If you don't want gestures to insert keys at negative time,
# set noNegativeKeys to "true".  The downside is that early
# gestures will not look as good if they are expressed at all.
# Also, early gestures may have a faster onset as suppression
# wears off, so you can't end the suppression too abruptly.
# Coarticulation curves from mapping may still create negative keys.
noNegativeKeys = getScriptSetting("gesturelib_noNegativeKeys", "false")

# The Normalized Power curve can be useful for opening the mouth wider
# on stresses syllables.
generateNormalizedPowerCurve = getScriptSetting("gesturelib_generateNormalizedPowerCurve", "false")

gestureLibName = "_HeadGestureLib"
issueCommand('animGroup -create -group "%s";' % (gestureLibName))

# Because this event group doesn't have an underscore, events from this group
# will be passed on from the analysis actor
#outputEventsGroup = "FxAnalysisEvents"
#issueCommand('animGroup -create -group "%s";'%(outputEventsGroup));

# A blank animation
EmptyAnim = Anim("Empty", gestureLibName)

AnimEventGroup = "_AnimEventGroup"
PhonemeEventGroup = "_PhonemeEventGroup"
StressEventGroup = "_StressEventGroup"
SilenceEventGroup = "_SilenceEventGroup"
# This group is for events we recognize in text tags.
TextEventGroup = "_TextEvents"
EmoticonEventGroup = "EmoticonEvents"
InternalEmoticonEventGroup = "_EmoticonEvents"

EmphasisHeadPitchName = "_Emphasis Head Pitch"
EmphasisHeadYawName = "_Emphasis Head Yaw"
EmphasisHeadRollName = "_Emphasis Head Roll"
OrientationHeadPitchName = "_Orientation Head Pitch"
OrientationHeadYawName = "_Orientation Head Yaw"
OrientationHeadRollName = "_Orientation Head Roll"
HeadPitchName = "Head Pitch"
HeadYawName = "Head Yaw"
HeadRollName = "Head Roll"
EyeYawName = "_Eye Yaw"
EyePitchName = "_Eye Pitch"
EyeYawCombinedName = "Eye Yaw"
EyePitchCombinedName = "Eye Pitch"
SquintName = "Squint"
EyebrowRaiseName = "Eyebrow Raise"
BlinkName = "Blink"
# By changing the names, we can change what curves are output.
if version_17X_Compatible == "true":
    EmphasisHeadPitchName = "Emphasis Head Pitch"
    EmphasisHeadYawName = "Emphasis Head Yaw"
    EmphasisHeadRollName = "Emphasis Head Roll"
    OrientationHeadPitchName = "Orientation Head Pitch"
    OrientationHeadYawName = "Orientation Head Yaw"
    OrientationHeadRollName = "Orientation Head Roll"
    HeadPitchName = "_Head Pitch"
    HeadYawName = "_Head Yaw"
    HeadRollName = "_Head Roll"
    EyeYawName = "Gaze Eye Yaw"
    EyePitchName = "Gaze Eye Pitch"
    EyeYawCombinedName = "_IGNORE_Eye Yaw"
    EyePitchCombinedName = "_IGNORE_Eye Pitch"
    SquintName = "_IGNORE_Squint"

animGroups = [AnimEventGroup, PhonemeEventGroup, StressEventGroup, SilenceEventGroup, TextEventGroup, EmoticonEventGroup, InternalEmoticonEventGroup]
for group in animGroups:
    issueCommand('animGroup -create -group "%s";' % (group))

AnimBegin = Anim("Anim_Begin", AnimEventGroup)
AnimEnd = Anim("Anim_End", AnimEventGroup)

headPitch = Anim(OrientationHeadPitchName, gestureLibName)
headYaw = Anim(OrientationHeadYawName, gestureLibName)
headRoll = Anim(OrientationHeadRollName, gestureLibName)
OrientationAnimations = [headPitch, headYaw, headRoll]

RandomOrientation = Anim("Random Orientation", gestureLibName)

OrientBlendin = .5
ZeroOrientation = Anim("Zero Orientation", gestureLibName)
ZeroOrientation.curves.append(OneSecondCurve("_Orientation_Correction", 1))
ZeroOrientation.buildAnim()
ZeroOrientationEvent = Event(ZeroOrientation.name, ZeroOrientation.group)
ZeroOrientationEvent.persist = "true"
ZeroOrientationEvent.inheritdur = "false"
ZeroOrientationEvent.inheritmag = "false"
ZeroOrientationEvent.set_blendin(OrientBlendin)
ZeroOrientationEvent.set_blendout(OrientBlendin)

for anim in OrientationAnimations:
    anim.curves.append(OneSecondCurve(anim.name, 1))
    anim.buildAnim()

# Head Pitch events are small and less likely because
# We move the head quite a bit in the pitch direction
# with emphasis events.
headPitchEvent = Event(headPitch.name, headPitch.group)
headPitchEvent.persist = "true"
headPitchEvent.minmagnitude = -1.5
headPitchEvent.maxmagnitude = 1.5
headPitchEvent.set_blendin(OrientBlendin)
headPitchEvent.set_blendout(OrientBlendin)
headPitchEvent.probability = .33
RandomOrientation.events.append(headPitchEvent)

headYawEvent = Event(headYaw.name, headYaw.group)
headYawEvent.persist = "true"
headYawEvent.minmagnitude = -2.5
headYawEvent.maxmagnitude = 2.5
headYawEvent.set_blendin(OrientBlendin)
headYawEvent.set_blendout(OrientBlendin)
headYawEvent.probability = .66
RandomOrientation.events.append(headYawEvent)

headRollEvent = Event(headRoll.name, headRoll.group)
headRollEvent.persist = "true"
headRollEvent.minmagnitude = -2.25
headRollEvent.maxmagnitude = 2.25
headRollEvent.set_blendin(OrientBlendin)
headRollEvent.set_blendout(OrientBlendin)
headRollEvent.probability = .66
RandomOrientation.events.append(headRollEvent)

RandomOrientation.buildAnim()

gazePitch = Anim(EyePitchName, gestureLibName)
gazeYaw = Anim(EyeYawName, gestureLibName)
RandomGaze = Anim("Random Gaze", gestureLibName)
GazeAnimations = [gazePitch, gazeYaw]
GazeMin = -1
GazeMax = 1
GazeProb = 1
GazeBlendin = .5
GazeDuration = .4
for anim in GazeAnimations:
    anim.curves.append(OneSecondCurve(anim.name, 1))
    anim.buildAnim()
    event = Event(anim.name, anim.group)
    event.persist = "true"
    event.inheritdur = "false"
    event.inheritmag = "false"
    event.minmagnitude = GazeMin
    event.maxmagnitude = GazeMax
    event.set_blendin(GazeBlendin)
    event.set_blendout(GazeBlendin)
    event.set_duration(GazeDuration)
    event.probability = GazeProb
    RandomGaze.events.append(event)
RandomGaze.buildAnim()

ZeroGaze = Anim("Zero Gaze", gestureLibName)
ZeroGaze.curves.append(OneSecondCurve("_Gaze_Correction", 1))
ZeroGazeEvent = Event(ZeroGaze.name, ZeroGaze.group)
ZeroGazeEvent.persist = "true"
ZeroGazeEvent.inheritdur = "false"
ZeroGazeEvent.inheritmag = "false"
ZeroGazeEvent.set_blendin(GazeBlendin)
ZeroGazeEvent.set_blendout(GazeBlendin)
ZeroGaze.buildAnim()

# make sure very short files don't have blink that forces the animation to be longer.
ZeroBlink = Anim("Zero Blink", gestureLibName)
ZeroBlink.curves.append(OneSecondCurve("_Blink_Correction", 1))
ZeroBlinkEvent = Event(ZeroBlink.name, ZeroBlink.group)
ZeroBlinkEvent.persist = "true"
ZeroBlinkEvent.set_blendin(.5)
ZeroBlinkEvent.set_blendout(.5)
ZeroBlinkEvent.inheritdur = "false"
ZeroBlinkEvent.inheritmag = "false"
ZeroBlinkEvent.set_duration(.4)
ZeroBlink.buildAnim()

# In most cases the final stress will close out the orientation shifts, but animations with
# only one stress will not have a final stress, so close out orientation shifts at AnimEnd.
AnimEnd.events.append(ZeroOrientationEvent)
AnimEnd.events.append(ZeroGazeEvent)
AnimEnd.events.append(ZeroBlinkEvent)
AnimEnd.buildAnim()

Squint = Anim("_Squint", gestureLibName)
SquintCurve = Curve("_Squint")
SquintCurve.keys.append(Key(gcSpeed * -.2867, 0))
SquintCurve.keys.append(Key(0, 1))
SquintCurve.keys.append(Key(gcSpeed * .5017, 0))
Squint.curves.append(SquintCurve)

EyebrowRaise = Anim("_Eyebrow Raise", gestureLibName)
EyebrowRaiseCurve = Curve("_Eyebrow Raise")
EyebrowRaiseCurve.keys.append(Key(gcSpeed * -.2867, 0))
EyebrowRaiseCurve.keys.append(Key(0, 1))
EyebrowRaiseCurve.keys.append(Key(gcSpeed * .5017, 0))
EyebrowRaise.curves.append(EyebrowRaiseCurve)

Blink = Anim("_Blink", gestureLibName)
BlinkCurve = Curve("_Blink")
BlinkCurve.keys.append(Key(-.125, 0))
BlinkCurve.keys.append(Key(0, 1))
BlinkCurve.keys.append(Key(.083, 0))
Blink.curves.append(BlinkCurve)

HeadNod = Anim(EmphasisHeadPitchName, gestureLibName)
HeadNodCurve = Curve(EmphasisHeadPitchName)
HeadNodCurve.keys.append(Key(gcSpeed * -.325, 0))
HeadNodCurve.keys.append(Key(0, 1))
HeadNodCurve.keys.append(Key(gcSpeed * .645, 0))
HeadNod.curves.append(HeadNodCurve)

HeadTilt = Anim(EmphasisHeadRollName, gestureLibName)
HeadTiltCurve = Curve(EmphasisHeadRollName)
HeadTiltCurve.keys.append(Key(gcSpeed * -.2867, 0))
HeadTiltCurve.keys.append(Key(0, 1))
HeadTiltCurve.keys.append(Key(gcSpeed * .645, 0))
HeadTilt.curves.append(HeadTiltCurve)

HeadTurn = Anim(EmphasisHeadYawName, gestureLibName)
HeadTurnCurve = Curve(EmphasisHeadYawName)
HeadTurnCurve.keys.append(Key(gcSpeed * -.2867, 0))
HeadTurnCurve.keys.append(Key(0, 1))
HeadTurnCurve.keys.append(Key(gcSpeed * .645, 0))
HeadTurn.curves.append(HeadTurnCurve)

EmphasisAnimations = [Squint, EyebrowRaise, Blink, HeadNod, HeadTilt, HeadTurn]

for anim in EmphasisAnimations:
    anim.buildAnim()

# The end of a silence is a good place for an orientation shift as it
# can signify a change in thought.  Long silences deliminate utterances
# and trigger Stress_Initial and Stress_Final stresses which are also
# good places for orientation shifts.
Silence_Medium = Anim("Silence_Medium", SilenceEventGroup)

orientationEvent = Event(RandomOrientation.name, RandomOrientation.group)
orientationEvent.probability = .8
orientationEvent.minstart = -.3
orientationEvent.maxstart = .3
orientationEvent.inheritdur = "false"
orientationEvent.inheritmag = "false"
orientationEvent.minduration = 1.5
orientationEvent.maxduration = 2
Silence_Medium.events.append(orientationEvent)

gazeEvent = Event(RandomGaze.name, RandomGaze.group)
gazeEvent.probability = .8
gazeEvent.minstart = .5
gazeEvent.maxstart = .9
gazeEvent.inheritdur = "false"
gazeEvent.inheritmag = "false"
Silence_Medium.events.append(gazeEvent)

Silence_Medium.buildAnim()

Silence_Short = Anim("Silence_Short", SilenceEventGroup)
Silence_Short.events.append(gazeEvent)
Silence_Short.buildAnim()

# We'll use a recursive anim to sprinkle blinks randomly throughout the
# animation.  Blinks can also occur during a stress.
recursiveAnim = Anim("recursive", gestureLibName)
blinkEvent = Event(Blink.name, Blink.group)
blinkEvent.probability = .8
recursiveAnim.events.append(blinkEvent)
recursiveEvent = Event(recursiveAnim.name, recursiveAnim.group)
recursiveEvent.minstart = 4
recursiveEvent.maxstart = 6
recursiveAnim.events.append(recursiveEvent)
recursiveAnim.buildAnim()

# Don't start our recursive blinks until we are well into the audio..
recursiveEvent.minstart = 1
recursiveEvent.maxstart = 3
AnimBegin.events.append(recursiveEvent)

if noNegativeKeys == "true":
    GestureSuppressionCurve = Curve("_Emphasis_Correction")
    # Don't set the first key unreasonably far back...it will increase baking times.
    GestureSuppressionCurve.keys.append(Key(-2, 1))
    GestureSuppressionCurve.keys.append(Key(0, 1))
    GestureSuppressionCurve.keys.append(Key(0.4, 0))
    AnimBegin.curves.append(GestureSuppressionCurve)
AnimBegin.buildAnim()

# make sure very short files don't have blink that forces the animation to be longer.
BlinkCorrection = Anim("_Blink_Correction", gestureLibName)
BlinkCorrection.curves.append(OneSecondCurve("_Blink_Correction", 1))
BlinkCorrection.buildAnim()

EmphasisBlinkProbability = .2

SCMinStart = 0
SCMaxStart = 0
SCMinDur = 1 * gcSpeed
SCMaxDur = 1 * gcSpeed
SCMinMag = 1 * gcMagnitude
SCMaxMag = 1 * gcMagnitude

# To compliment head movements, we can either squint or raise eyebrows, but not both.
EyebrowSquintPick1 = Anim("EyebrowSquintPick1", gestureLibName)
EyebrowSquintPick1.groupChildEvents = "true"
eyebrowEvent = Event(EyebrowRaise.name, EyebrowRaise.group)
eyebrowEvent.probability = .7
eyebrowEvent.minstart = SCMinStart
eyebrowEvent.maxstart = SCMaxStart
eyebrowEvent.minduration = SCMinDur
eyebrowEvent.maxduration = SCMaxDur
eyebrowEvent.minmagnitude = SCMinMag * .3
eyebrowEvent.maxmagnitude = SCMaxMag * .6
eyebrowEvent.weight = 2
EyebrowSquintPick1.events.append(eyebrowEvent)
squintEvent = copy.deepcopy(eyebrowEvent)
squintEvent.name = Squint.name
squintEvent.minmagnitude = SCMinMag * .3
squintEvent.maxmagnitude = SCMaxMag * .5
squintEvent.probability = .5
squintEvent.weight = 1
EyebrowSquintPick1.events.append(squintEvent)
EyebrowSquintPick1.buildAnim()

EyebrowSquintPick1Event = Event(EyebrowSquintPick1.name, EyebrowSquintPick1.group)
BlinkEvent = Event(Blink.name, Blink.group)
BlinkEvent.probability = .05

SC_Initial = Anim("Stress_Initial", StressEventGroup)
SC_Quick = Anim("Stress_Quick", StressEventGroup)
SC_Normal = Anim("Stress_Normal", StressEventGroup)
SC_Isolated = Anim("Stress_Isolated", StressEventGroup)
SC_Final = Anim("Stress_Final", StressEventGroup)

# Close out the Orientation and Gaze at the final stress.
SC_Final.events.append(ZeroOrientationEvent)
SC_Final.events.append(ZeroGazeEvent)

# Start our gestures off with an orientation shift, but a smaller one than
# usual as we are also going to have Emphasis movement.
orientationEvent.set_magnitude(.7)
orientationEvent.minstart = 0
orientationEvent.maxstart = 0
SC_Initial.events.append(orientationEvent)

ActivateOrientation = copy.deepcopy(ZeroOrientationEvent)
ActivateOrientation.set_magnitude(0)
ActivateOrientation.set_start(-ActivateOrientation.maxblendin)
ActivateGaze = copy.deepcopy(ZeroGazeEvent)
ActivateGaze.set_magnitude(0)
ActivateGaze.set_start(-ActivateGaze.maxblendin)
SC_Initial.events.append(ActivateOrientation)
SC_Initial.events.append(ActivateGaze)

StrongHeadNodEvent = Event(HeadNod.name, HeadNod.group)
StrongHeadNodEvent.minstart = SCMinStart
StrongHeadNodEvent.maxstart = SCMaxStart
StrongHeadNodEvent.minduration = SCMinDur
StrongHeadNodEvent.maxduration = SCMaxDur
StrongHeadNodEvent.minmagnitude = 4 * SCMinMag
StrongHeadNodEvent.maxmagnitude = 4 * SCMaxMag

InvertedHeadNodEvent = Event(HeadNod.name, HeadNod.group)
InvertedHeadNodEvent.minstart = SCMinStart
InvertedHeadNodEvent.maxstart = SCMaxStart
InvertedHeadNodEvent.minduration = 1.2 * SCMinDur
InvertedHeadNodEvent.maxduration = 1.2 * SCMaxDur
InvertedHeadNodEvent.minmagnitude = -2.4 * SCMinMag
InvertedHeadNodEvent.maxmagnitude = -2.4 * SCMaxMag

NormalHeadNodEvent = Event(HeadNod.name, HeadNod.group)
NormalHeadNodEvent.minstart = SCMinStart
NormalHeadNodEvent.maxstart = SCMaxStart
NormalHeadNodEvent.minduration = 1.2 * SCMinDur
NormalHeadNodEvent.maxduration = 1.2 * SCMaxDur
NormalHeadNodEvent.minmagnitude = 2.4 * SCMinMag
NormalHeadNodEvent.maxmagnitude = 2.4 * SCMaxMag

QuickHeadNodEvent = Event(HeadNod.name, HeadNod.group)
QuickHeadNodEvent.minstart = SCMinStart
QuickHeadNodEvent.maxstart = SCMaxStart
QuickHeadNodEvent.minduration = .8 * SCMinDur
QuickHeadNodEvent.maxduration = .8 * SCMaxDur
QuickHeadNodEvent.minmagnitude = 1.6 * SCMinMag
QuickHeadNodEvent.maxmagnitude = 1.6 * SCMaxMag

QuickInvertedNodEvent = Event(HeadNod.name, HeadNod.group)
QuickInvertedNodEvent.minstart = SCMinStart
QuickInvertedNodEvent.maxstart = SCMaxStart
QuickInvertedNodEvent.minduration = .8 * SCMinDur
QuickInvertedNodEvent.maxduration = .8 * SCMaxDur
QuickInvertedNodEvent.minmagnitude = -1.6 * SCMinMag
QuickInvertedNodEvent.maxmagnitude = -1.6 * SCMaxMag

EmptyEvent = Event(EmptyAnim.name, EmptyAnim.group)

HeadTiltEvent = Event(HeadTilt.name, HeadTilt.group)
HeadTiltEvent.minstart = SCMinStart
HeadTiltEvent.maxstart = SCMaxStart
HeadTiltEvent.minduration = SCMinDur
HeadTiltEvent.maxduration = SCMaxDur
HeadTiltEvent.minmagnitude = 1.6 * SCMinMag
HeadTiltEvent.maxmagnitude = 1.6 * SCMaxMag

NegHeadTiltEvent = Event(HeadTilt.name, HeadTilt.group)
NegHeadTiltEvent.minstart = SCMinStart
NegHeadTiltEvent.maxstart = SCMaxStart
NegHeadTiltEvent.minduration = SCMinDur
NegHeadTiltEvent.maxduration = SCMaxDur
NegHeadTiltEvent.minmagnitude = -1.6 * SCMinMag
NegHeadTiltEvent.maxmagnitude = -1.6 * SCMaxMag

HeadTurnEvent = Event(HeadTurn.name, HeadTurn.group)
HeadTurnEvent.minstart = SCMinStart
HeadTurnEvent.maxstart = SCMaxStart
HeadTurnEvent.minduration = SCMinDur
HeadTurnEvent.maxduration = SCMaxDur
HeadTurnEvent.minmagnitude = 1.6 * SCMinMag
HeadTurnEvent.maxmagnitude = 1.6 * SCMaxMag

NegHeadTurnEvent = Event(HeadTurn.name, HeadTurn.group)
NegHeadTurnEvent.minstart = SCMinStart
NegHeadTurnEvent.maxstart = SCMaxStart
NegHeadTurnEvent.minduration = SCMinDur
NegHeadTurnEvent.maxduration = SCMaxDur
NegHeadTurnEvent.minmagnitude = -1.6 * SCMinMag
NegHeadTurnEvent.maxmagnitude = -1.6 * SCMaxMag

# An convenient event for any stress
SC_ALL = Anim("Stress_All", StressEventGroup)
SC_ALL.events.append(EyebrowSquintPick1Event)
SC_ALL.events.append(BlinkEvent)
SC_ALL.buildAnim()
SC_ALL_Event = Event(SC_ALL.name, SC_ALL.group)

StressCtgries = [SC_Initial, SC_Quick, SC_Normal, SC_Isolated, SC_Final]

pick1Anims = []
for sc in StressCtgries:
    pick1Anim = Anim(sc.name + "_Pick1", gestureLibName)
    pick1Anim.groupChildEvents = "true"
    pick1AnimEvent = Event(pick1Anim.name, pick1Anim.group)
    pick1Anim.group = gestureLibName
    pick1Anims.append(pick1Anim)
    sc.events.append(pick1AnimEvent)
    sc.events.append(SC_ALL_Event)
    sc.buildAnim()


EAs = [StrongHeadNodEvent, InvertedHeadNodEvent, QuickHeadNodEvent, NormalHeadNodEvent, EmptyEvent, HeadTiltEvent, NegHeadTiltEvent, HeadTurnEvent, NegHeadTurnEvent]

# SC_Initial
weights = [.33, .17, .03, .13, .1, .05, .05, .06, .06]
i = 0
for EA in EAs:
    EA.weight = weights[i]
    pick1Anims[0].events.append(EA)
    i += 1
pick1Anims[0].buildAnim()

# SC_Quick
weights = [0, .1, .3, .09, .2, .1, .1, .1, .1]
i = 0
for EA in EAs:
    EA.weight = weights[i]
    pick1Anims[1].events.append(EA)
    i += 1
pick1Anims[1].buildAnim()

# SC_Normal
weights = [.04, .14, .1, .36, .1, .075, .075, .075, .075]
i = 0
for EA in EAs:
    EA.weight = weights[i]
    pick1Anims[2].events.append(EA)
    i += 1
pick1Anims[2].buildAnim()

# SC_Isolated
weights = [.23, .20, .1, .17, .1, .05, .05, .05, .05]
i = 0
for EA in EAs:
    EA.weight = weights[i]
    pick1Anims[3].events.append(EA)
    i += 1
pick1Anims[3].buildAnim()

# SC_Final
weights = [.33, .10, .07, .24, .15, .015, .015, .035, .035]
i = 0
for EA in EAs:
    EA.weight = weights[i]
    pick1Anims[4].events.append(EA)
    i += 1
pick1Anims[4].buildAnim()

emoticonSupport = "true"
EmoticonNodePrefix = "_Emoticon "
# Emoticons
# The emoticon system allows the artist to use combinations of punctuation markers
# to trigger animations.  The below emoticons
if emoticonSupport == "true" and version_17X_Compatible == "false":
    emotions = [["happy", ":)"], ["sad", ":("], ["angry", ";("], ["surprised", ":@"]]
    for emotion in emotions:
        emotionAnim = Anim(emotion[0], InternalEmoticonEventGroup)
        emoticonAnim = Anim(emotion[1],  EmoticonEventGroup)
        emotionAnim.curves.append(OneSecondCurve(emotion[0], 1))
        emotionAnimEvent = Event(emotion[0], InternalEmoticonEventGroup)
        emotionAnimEvent.set_blendin(.2)
        emotionAnimEvent.set_blendout(.2)
        emotionAnimEvent.blendunscaled = "true"
        emoticonAnim.events.append(emotionAnimEvent)
        emoticonAnim.buildAnim()
        emotionAnim.buildAnim()

    # __ emoticon turns off speech gestures
    emphasisCorrectionAnim = Anim("_Emphasis_Correction",  InternalEmoticonEventGroup)
    emphasisCorrectionAnim.curves.append(OneSecondCurve("_Emphasis_Correction", 1))
    emphasisCorrectionAnim.buildAnim()
    emphasisCorrectionEvent = Event(emphasisCorrectionAnim.name, emphasisCorrectionAnim.group)
    # This needs to be very slow, otherwise if can cause jerkey animation
    emphasisCorrectionEvent.set_blendin(1)
    emphasisCorrectionEvent.set_blendin(1)
    emphasisCorrectionEvent.blendunscaled = "true"
    emoticonAnim = Anim("__",  EmoticonEventGroup)
    emoticonAnim.events.append(emphasisCorrectionEvent)
    emoticonAnim.buildAnim()

    oneSecondEmoticonAnimNames = [HeadPitchName, HeadYawName, HeadRollName, EyePitchCombinedName, EyeYawCombinedName, SquintName, EyebrowRaiseName, BlinkName, "_Emphasis_Correction"]
    for oneSecondEmoticonAnimName in oneSecondEmoticonAnimNames:
        oneSecondEmoticonAnim = Anim(EmoticonNodePrefix + oneSecondEmoticonAnimName, InternalEmoticonEventGroup)
        oneSecondEmoticonAnim.curves.append(OneSecondCurve(EmoticonNodePrefix + oneSecondEmoticonAnimName, 1))
        oneSecondEmoticonAnim.buildAnim()

    # %^ look away up
    # %- look away right
    # -% look away left
    # %_ look away down
    # emoticon name, eye-yaw magnitude, eye-pitch magnitude
    lookaways = [["%^", 0, -20], ["%-", 20, 0], ["-%", -20, 0], ["%_", 0, 20]]
    for lookaway in lookaways:
        emoticonAnim = Anim(lookaway[0],  EmoticonEventGroup)
        EmoticonEyePitchEvent = Event(EmoticonNodePrefix + EyePitchCombinedName, InternalEmoticonEventGroup)
        EmoticonEyePitchEvent.set_magnitude(lookaway[2])
        EmoticonEyePitchEvent.set_blendin(.2)
        EmoticonEyePitchEvent.set_blendout(.2)
        EmoticonEyePitchEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonEyePitchEvent)
        EmoticonEyeYawEvent = Event(EmoticonNodePrefix + EyeYawCombinedName, InternalEmoticonEventGroup)
        EmoticonEyeYawEvent.set_magnitude(lookaway[1])
        EmoticonEyeYawEvent.set_blendin(.2)
        EmoticonEyeYawEvent.set_blendout(.2)
        EmoticonEyeYawEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonEyeYawEvent)
        emoticonAnim.buildAnim()

    # #- head turn right
    # -# head turn left
    # #^ head turn up
    # #_ head turn down
    # =# head roll right
    # #= head roll left

    headturns = [["#^", 0, -10, 0], ["#-", 10, 0, 0], ["-#", -10, 0, 0], ["#_", 0, 10, 0], ["#=", 0, 0, 10], ["=#", 0, 0, -10]]
    for headturn in headturns:
        emoticonAnim = Anim(headturn[0],  EmoticonEventGroup)
        EmoticonHeadPitchEvent = Event(EmoticonNodePrefix + HeadPitchName, InternalEmoticonEventGroup)
        EmoticonHeadPitchEvent.set_magnitude(headturn[2])
        EmoticonHeadPitchEvent.set_blendin(.5)
        EmoticonHeadPitchEvent.set_blendout(.5)
        EmoticonHeadPitchEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonHeadPitchEvent)

        EmoticonHeadYawEvent = Event(EmoticonNodePrefix + HeadYawName, InternalEmoticonEventGroup)
        EmoticonHeadYawEvent.set_magnitude(headturn[1])
        EmoticonHeadYawEvent.set_blendin(.5)
        EmoticonHeadYawEvent.set_blendout(.5)
        EmoticonHeadYawEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonHeadYawEvent)

        EmoticonHeadRollEvent = Event(EmoticonNodePrefix + HeadRollName, InternalEmoticonEventGroup)
        EmoticonHeadRollEvent.set_magnitude(headturn[3])
        EmoticonHeadRollEvent.set_blendin(.5)
        EmoticonHeadRollEvent.set_blendout(.5)
        EmoticonHeadRollEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonHeadRollEvent)

        emoticonAnim.buildAnim()
    # emoticon, eyebrow, squint
    # @@ wide eyes
    # -- squint
    # (&  eyebrows up
    # )&  eyebrows down
    eyeAnims = [["(&", .8, 0], [")&", -.8, 0], ["@@", .5, -.5], ["--", -.2, .5]]
    for eyeAnim in eyeAnims:
        emoticonAnim = Anim(eyeAnim[0],  EmoticonEventGroup)
        EmoticonEyebrowEvent = Event(EmoticonNodePrefix + EyebrowRaiseName, InternalEmoticonEventGroup)
        EmoticonEyebrowEvent.set_magnitude(eyeAnim[1])
        EmoticonEyebrowEvent.set_blendin(.3)
        EmoticonEyebrowEvent.set_blendout(.3)
        EmoticonEyebrowEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonEyebrowEvent)

        EmoticonSquintEvent = Event(EmoticonNodePrefix + SquintName, InternalEmoticonEventGroup)
        EmoticonSquintEvent.set_magnitude(eyeAnim[2])
        EmoticonSquintEvent.set_blendin(.3)
        EmoticonSquintEvent.set_blendout(.3)
        EmoticonSquintEvent.blendunscaled = "true"
        emoticonAnim.events.append(EmoticonSquintEvent)
        emoticonAnim.buildAnim()
# FaceFX Studio can insert text tags when certain words are spoken.  Inserting a
# "Negative" event when a negative word is spoken looks good if the negative word
# triggers a head shake.  We supress normal based gestures when we do this.
# You need to set up a analysis text preprocessor python callback to make use of
# this.  Also, it requires modifications to work with 1.7.X compatible setups,
# becuase it keys the "Head Yaw" curve directly.
textTagEvents = "true"
if textTagEvents == "true" and version_17X_Compatible == "false":
    # We don't want the head shake geting suppressed along with the normal gestures,
    # So key the output curve directly.
    headShakeAnim = Anim(HeadYawName, TextEventGroup)
    headShakeCurve = Curve(HeadYawName)
    # Don't set the first key unreasonably far back...it will increase baking times.
    headShakeCurve.keys.append(Key(-.2, 0))
    headShakeCurve.keys.append(Key(0, 2.5))
    headShakeCurve.keys.append(Key(.2, 0))
    headShakeAnim.curves.append(headShakeCurve)
    orientationEvent.set_start(-.15)
    headShakeAnim.events.append(orientationEvent)
    headShakeAnim.buildAnim()

    emphasisCorrectionAnim = Anim("_Emphasis_Correction", TextEventGroup)
    emphasisCorrectionCurve = Curve("_Emphasis_Correction")
    # Don't set the first key unreasonably far back...it will increase baking times.
    emphasisCorrectionCurve.keys.append(Key(-.5, 0))
    emphasisCorrectionCurve.keys.append(Key(-.15, 1))
    emphasisCorrectionCurve.keys.append(Key(.15, 1))
    emphasisCorrectionCurve.keys.append(Key(.5, 0))
    emphasisCorrectionAnim.curves.append(emphasisCorrectionCurve)
    emphasisCorrectionAnim.buildAnim()
    emphasisCorrectionEvent = Event(emphasisCorrectionAnim.name, emphasisCorrectionAnim.group)
    emphasisCorrectionEvent.inheritmag = "false"

    headShakeEvent = Event(headShakeAnim.name, headShakeAnim.group)
    headShakePosNegAnim = Anim("Head Yaw PosNeg", TextEventGroup)
    headShakePosNegAnim.groupChildEvents = "true"
    headShakePosNegAnim.events.append(headShakeEvent)
    inverseHeadShakeEvent = copy.deepcopy(headShakeEvent)
    inverseHeadShakeEvent.set_magnitude(-1)
    headShakePosNegAnim.events.append(inverseHeadShakeEvent)
    headShakePosNegAnim.buildAnim()
    headShakePosNegAnimEvent = Event(headShakePosNegAnim.name, headShakePosNegAnim.group)

    negativeHeadShakeAnim = Anim("Negative Head Shake", TextEventGroup)
    negativeHeadShakeAnim.events.append(emphasisCorrectionEvent)
    negativeHeadShakeAnim.events.append(Event(headShakePosNegAnimEvent.name, headShakePosNegAnimEvent.group))
    negativeHeadShakeAnim.buildAnim()
    negativeHeadShakeEvent = Event(negativeHeadShakeAnim.name, negativeHeadShakeAnim.group)

    # Make a copy of some other events, but make them act on the output nodes, not
    # on the ones that are supressed with _Emphasis_Correction
    EyebrowSquintPick1_noCorrection = copy.deepcopy(EyebrowSquintPick1)
    EyebrowRaise_noCorrection = copy.deepcopy(EyebrowRaise)
    Squint_noCorrection = copy.deepcopy(Squint)
    copyanims = [EyebrowRaise_noCorrection, Squint_noCorrection, EyebrowSquintPick1_noCorrection]
    for anim in copyanims:
        anim.name = anim.name.lstrip('_')
        anim.group = TextEventGroup
        issueCommand('anim -add -group "%s" -name "%s";' % (anim.group, anim.name))
        for curve in anim.curves:
            curve.name = curve.name.lstrip('_')
        for event in anim.events:
            event.name = event.name.lstrip('_')
            event.group = TextEventGroup
        anim.buildAnim()

    # Add some variability
    negativeHeadShakeEvent.minstart = -.1
    negativeHeadShakeEvent.maxstart = .1
    negativeHeadShakeEvent.minduration = .9
    negativeHeadShakeEvent.maxduration = 1.1
    negativeHeadShakeEvent.minmagnitude = .9
    negativeHeadShakeEvent.maxmagnitude = 1.1
    EyebrowSquintPick1_noCorrectionEvent = Event(EyebrowSquintPick1_noCorrection.name, EyebrowSquintPick1_noCorrection.group)
    EyebrowSquintPick1_noCorrectionEvent.minstart = -.1
    EyebrowSquintPick1_noCorrectionEvent.maxstart = .1
    EyebrowSquintPick1_noCorrectionEvent.minduration = .9
    EyebrowSquintPick1_noCorrectionEvent.maxduration = 1.1
    EyebrowSquintPick1_noCorrectionEvent.minmagnitude = .9
    EyebrowSquintPick1_noCorrectionEvent.maxmagnitude = 1.1
    negativeAnim = Anim("Negative", TextEventGroup)
    negativeAnim.events.append(EyebrowSquintPick1_noCorrectionEvent)
    negativeAnim.events.append(negativeHeadShakeEvent)
    negativeAnim.buildAnim()

issueCommand('batch;')

rotationOutputCurves = [HeadPitchName, HeadRollName, HeadYawName, EyePitchCombinedName, EyeYawCombinedName]
eyeOutputCurves = [EyebrowRaiseName, BlinkName, SquintName]
emotionOutputCurves = ["happy", "sad", "angry", "surprised"]

# We can run this script on an existing actor to use it in conjunction with the <Events Only> analysis actor.
# In this scenario, we'll skip the creation of the output combiner nodes because we assume they exist in the actor
# If they don't exist in the actor, this script will output errors at the very end.
if getNumFaceGraphNodes() == 0:
    for curve in rotationOutputCurves:
        issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -30 -max 30;' % (curve))
    for curve in eyeOutputCurves:
        issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -1 -max 1;' % (curve))
    for curve in emotionOutputCurves:
        issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min 0 -max 1;' % (curve))

if generateNormalizedPowerCurve == "true":
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Analysis_Normalized_Power"')
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "Normalized Power"')
    # FaceFX does a poor job baking the Normalized power curve (or any jittery curve), so create
    # create a small face graph setup to remove useless keys by ensuring that all values below .01 are
    # forced to 0.
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_reduce0keysAdd"')
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_reduce0keys"')
    issueCommand('graph -link -from "_Analysis_Normalized_Power" -to "_reduce0keysAdd" -linkfn "clamped linear" -linkfnparams "m=1000|clampx=0.010000|clampy=0.010000|clampdir=-1.000000"')
    issueCommand('graph -link -from "_Analysis_Normalized_Power" -to "_reduce0keys" -linkfn "linear" -linkfnparams "m=1.000000|b=-0.010000"')
    issueCommand('graph -link -from "_reduce0keys" -to "Normalized Power" -linkfn "linear"')
    issueCommand('graph -link -from "_reduce0keysAdd" -to "Normalized Power" -linkfn "linear"')

issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (OrientationHeadPitchName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (OrientationHeadRollName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (OrientationHeadYawName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (EmphasisHeadPitchName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (EmphasisHeadRollName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (EmphasisHeadYawName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (EyePitchName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -10 -max 10;' % (EyeYawName))
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Eyebrow Raise";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Blink";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Squint";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_All_Correction";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Emphasis_Correction";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Blink_Correction";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Orientation_Correction";')
issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "_Gaze_Correction";')

for curve in rotationOutputCurves:
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -30 -max 30;' % (EmoticonNodePrefix + curve))
    issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EmoticonNodePrefix + curve, curve))

for curve in eyeOutputCurves:
    issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -min -1 -max 1;' % (EmoticonNodePrefix + curve))
    issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EmoticonNodePrefix + curve, curve))

issueCommand('graph -link -from "_All_Correction" -to "_Emphasis_Correction" -linkfn "linear";')
issueCommand('graph -link -from "_All_Correction" -to "_Blink_Correction" -linkfn "linear";')
issueCommand('graph -link -from "_All_Correction" -to "_Orientation_Correction" -linkfn "linear";')
issueCommand('graph -link -from "_All_Correction" -to "_Gaze_Correction" -linkfn "linear";')
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EmphasisHeadPitchName, HeadPitchName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EmphasisHeadYawName, HeadYawName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EmphasisHeadRollName, HeadRollName))
issueCommand('graph -link -from "_Blink" -to "%s" -linkfn "linear";' % (BlinkName))
issueCommand('graph -link -from "_Eyebrow Raise" -to "%s" -linkfn "linear";' % (EyebrowRaiseName))
issueCommand('graph -link -from "_Squint" -to "%s" -linkfn "linear";' % (SquintName))
issueCommand('graph -link -from "_Emphasis_Correction" -to "%s" -linkfn "corrective";' % (EmphasisHeadPitchName))
issueCommand('graph -link -from "_Emphasis_Correction" -to "%s" -linkfn "corrective";' % (EmphasisHeadYawName))
issueCommand('graph -link -from "_Emphasis_Correction" -to "%s" -linkfn "corrective";' % (EmphasisHeadRollName))
issueCommand('graph -link -from "_Emphasis_Correction" -to "_Squint" -linkfn "corrective";')
issueCommand('graph -link -from "_Emphasis_Correction" -to "_Eyebrow Raise" -linkfn "corrective";')
issueCommand('graph -link -from "_Emphasis_Correction" -to "_Blink_Correction" -linkfn "linear";')
issueCommand('graph -link -from "_Blink_Correction" -to "_Blink" -linkfn "corrective";')
issueCommand('graph -link -from "_Orientation_Correction" -to "%s" -linkfn "corrective";' % (OrientationHeadPitchName))
issueCommand('graph -link -from "_Orientation_Correction" -to "%s" -linkfn "corrective";' % (OrientationHeadYawName))
issueCommand('graph -link -from "_Orientation_Correction" -to "%s" -linkfn "corrective";' % (OrientationHeadRollName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (OrientationHeadPitchName, HeadPitchName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (OrientationHeadYawName, HeadYawName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (OrientationHeadRollName, HeadRollName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "negate";' % (HeadPitchName, EyePitchCombinedName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "negate";' % (HeadYawName, EyeYawCombinedName))

issueCommand('graph -link -from "_Gaze_Correction" -to "%s" -linkfn "corrective";' % (EyePitchName))
issueCommand('graph -link -from "_Gaze_Correction" -to "%s" -linkfn "corrective";' % (EyeYawName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EyePitchName, EyePitchCombinedName))
issueCommand('graph -link -from "%s" -to "%s" -linkfn "linear";' % (EyeYawName, EyeYawCombinedName))
issueCommand('execBatch -editednodes;')
