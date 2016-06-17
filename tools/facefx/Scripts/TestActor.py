# This script will display a message box with some warnings about the actor if any potential problems are
# discovered.


from FxStudio import *
from FxAnimation import *
import FxPhonemes

displayWarningMessage = 0
warningMessage = "Take a look at the following warnings:"

# Find out if all of our
nodeNames = getFaceGraphNodeNames()
phonemeMap = FxPhonemes.PhonemeMap()

lowercaseNodes = []
for node in nodeNames:
    lowercaseNodes.append(node.lower())

displayCapGestureError = 0
displayNoGestureError = 0
capGestureError = "The following speech gesture targets in the default analysis actor do not have corresponding nodes, but a node exists with different captalization: "
noGestureError = "The following speech gesture targets in the default analysis actor are not contained in this actor: "
for entry in ["Blink", "Eye Pitch", "Eye Yaw", "Eyebrow Raise", "Head Pitch", "Head Roll", "Head Yaw", "Squint"]:
    print nodeNames.count(entry)
    if nodeNames.count(entry) == 0:
        if 1 == lowercaseNodes.count(entry.lower()):
            displayCapGestureError = 1
            capGestureError += entry + ", "
        else:
            displayNoGestureError = 1
            noGestureError += entry + ", "

if 1 == displayNoGestureError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + noGestureError.rstrip(', ')

if 1 == displayCapGestureError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + capGestureError.rstrip(', ')

visemeTable = {}
numTargets = 0
for entry in phonemeMap.entries:
    visemeTable[entry.targetName] = 0
    numTargets += 1

if numTargets == 0:
    displayWarningMessage = 1
    warningMessage += "\n\n" + "No mapping is defined."

displayCapSpeechError = 0
displayNoSpeechError = 0
capSpeechError = "The following speech targets in the mapping do not have corresponding nodes, but a node exists with different captialization: "
noSpeechError = "The following speech targets in the mapping are not contained in this actor: "

for entry in visemeTable.keys():
    if nodeNames.count(entry) ==  0:
        if 1 == lowercaseNodes.count(entry.lower()):
            displayCapSpeechError = 1
            capSpeechError += entry + ", "
        else:
            displayNoSpeechError = 1
            noSpeechError += entry + ", "

if 1 == displayNoSpeechError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + noSpeechError.rstrip(', ')

if 1 == displayCapSpeechError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + capSpeechError.rstrip(', ')


noBonesError = "The following bone poses are identical to the reference pose and contain no bones: "
displayNoBonesError = 0
for name in nodeNames:
    props = getFaceGraphNodeProperties(name)
    if props[0] == 'FxBonePoseNode':
        if len(getBonePoseBoneNames(name)) == 0:
            displayNoBonesError = 1
            noBonesError += name + ", "
if 1 == displayNoBonesError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + noBonesError.rstrip(', ')

displayBoneCurveError = 0
boneCurveError = "Bone curve nodes detected.  A curve with the same name as a bone will activate or deactivate the bone in the animation.  See the documentation for bone curves for more information.   The following nodes have the same name as a bone in the actor: "

refBoneNames = []
refBonesAndNodes = getFaceGraphNodeNames()
refBoneStruct = getBoneRefFrame()

if len(refBoneStruct) == 0:
    displayWarningMessage = 1
    warningMessage += "\n\n" + "The reference pose is empty."

for struct in refBoneStruct:
    if refBonesAndNodes.count(struct[0]) == 1:
        displayBoneCurveError = 1
        boneCurveError += struct[0] + ", "
        refBoneNames.append(struct[0])

if 1 == displayBoneCurveError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + boneCurveError.rstrip(', ')

displayMorphError = 0
morphError = "Morph targets are being driven by more than one node.  The result is not summed, so the morph target will be driven by the last node evaluated.  Each target should only be driven by a single node.  The following targets may not be evaluated correctly: "
morphTargetNames = []
for name in nodeNames:
    props = getFaceGraphNodeProperties(name)
    if props[0] == 'FxMorphTargetNode':
        if morphTargetNames.count(props[4][0][2]) == 1:
            displayMorphError = 1
            morphError += props[4][0][2] + ", "
        morphTargetNames.append(props[4][0][2])

if 1 == displayMorphError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + morphError.rstrip(', ')

keyError = "Duplicate keys detected (Duplicate keys share the same time value). Duplicate keys can evaluate unpredictably, especially when their values differ.  Take a look at the following curves: "
displayKeyError = 0
animationNames = getAnimationNames()
for group in animationNames:
    for anim in group[1]:
        curves = getCurveNames(group[0], anim)
        for curve in curves:
            keys = getKeys(group[0], anim, curve)
            # set lastkeytime to the animation end time plus something, so it won't match.
            lastkeytime = getAnimationProperties(group[0], anim)[1] + 1
            for key in keys:
                if key[0] == lastkeytime:
                    displayKeyError = 1
                    keyError += group[0] + "|" + anim + "|" + curve + ", "
                lastkeytime = key[0]

if 1 == displayKeyError:
    displayWarningMessage = 1
    warningMessage += "\n\n" + keyError.rstrip(', ')


if 1 == displayWarningMessage:
    warnBox(warningMessage)
else:
    msgBox("The loaded actor has no warnings. Good job!")
