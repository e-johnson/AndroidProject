""" Various routines to support debugging.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import *
from FxFaceGraph import *
from FxBone import *
from FxAnimation import *
from FxPhonemes import *
import os.path


def searchForBone(boneName):
    """
    Finds all references to the bone named boneName. This includes the
    reference pose and all bone poses.
    """
    boneList = getBoneNames()

    try:
        boneList.index(boneName)
    except ValueError:
        print 'The bone \"' + boneName + '\" is not controlled by FaceFX.'
        return

    referencePose = ReferencePose()
    faceGraph = FaceGraph()
    bonePoses = [BonePose(n.name) for n in faceGraph.nodes if n.type == 'FxBonePoseNode']

    print '\n'

    for bone in referencePose.bones:
        if bone.name == boneName:
            print 'Reference Pose:'
            print '\t' + str(bone)

    for pose in bonePoses:
        for bone in pose.bones:
            if bone.name == boneName:
                print pose.name + ':'
                print '\t' + str(bone)


def postAnalysisDumpRawFile(animGroup, animName):
    absoluteAudioAssetPath = Animation(animGroup, animName).absoluteAudioAssetPath
    rawFilePath = absoluteAudioAssetPath.replace(os.path.splitext(absoluteAudioAssetPath)[1], '.raw')
    selectAnimation(animGroup, animName)
    issueCommand('developer -saveaudiofile \"%s\"' % rawFilePath)


def createRawFilesWhenAnalyzing():
    connectSignal('postanalysis', postAnalysisDumpRawFile)


def makeOneToOnePhonemeMapping():
    # First get the current phoneme mapping.
    currentMapping = PhonemeMap()

    issueCommand('batch')

    # Remove all targets from the current mapping.
    for targetName in currentMapping.getTargetNamesUsedInMapping():
        issueCommand('map -remove -track "{0}"'.format(targetName))

    # Add face graph nodes for each phoneme along with tracks in the mapping
    # with weights of 1.
    for phoneme in PHONEME_REGISTRY.entries:
        issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "{0}"'.format(phoneme.facefxCoding))
        issueCommand('map -create -track "{0}" -type "basic"'.format(phoneme.facefxCoding))
        issueCommand('map -set -phoneme "{0}" -track "{0}" -value 1.0"'.format(phoneme.facefxCoding))

    issueCommand('execBatch -changedmapping -addednodes')

    issueCommand('graph -layout')


def getEventTemplateEventIDs(animGroup, animName):
    anim = Animation(animGroup, animName)
    return [e.eventID for ceg in anim.eventTemplate.childEventGroups for e in ceg.childEvents]


def getDuplicateEventTemplateEventIDs(animGroup, animName):
    eventIDs = getEventTemplateEventIDs(animGroup, animName)
    eventID_set = set()
    addToEventID_set = eventID_set.add
    duplicates = set(id for id in eventIDs if id in eventID_set or addToEventID_set(id))
    return list(duplicates)
