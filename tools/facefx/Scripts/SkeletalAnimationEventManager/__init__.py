""" Handles skeletal animation payloads in events.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""
from FxStudio import *
from FxAnimation import *
import string
import re

_SKELETAL_ANIMATION_EVENT_MANAGER_VERSION = '1.0'
_SKELETAL_ANIMATION_EVENT_MANAGER_AUTHOR = 'OC3 Entertainment'
_SKELETAL_ANIMATION_EVENT_MANAGERR_DESC = 'Manages skeletal animations triggered via event payloads.'


def info():
    """ Return the tuple with information about the plugin.

    This is a __facefx__ native plugin, meaning it will default to being
    loaded on a fresh install of FaceFX Studio.

    """
    return (_SKELETAL_ANIMATION_EVENT_MANAGER_VERSION, _SKELETAL_ANIMATION_EVENT_MANAGER_AUTHOR, _SKELETAL_ANIMATION_EVENT_MANAGERR_DESC)


def load():
    """ Loads the plugin. """
    # Hook our functions into their corresponding FaceFX Studio Python signals.
    connectSignal('animationselectionchanged', SkeletalAnimationEventManager_onAnimationChanged)
    connectSignal('posteventtakecreation', SkeletalAnimationEventManager_onPostEventTakeCreation)
    connectSignal('previewanimationsettingschanged', SkeletalAnimationEventManager_onPreviewAnimationSettingsChanged)
    connectSignal('renderassetloaded', SkeletalAnimationEventManager_onRenderAssetLoaded)


def unload():
    """ Unloads the plugin. """
    # Disconnect our signal handlers.
    disconnectSignal('animationselectionchanged', SkeletalAnimationEventManager_onAnimationChanged)
    disconnectSignal('posteventtakecreation', SkeletalAnimationEventManager_onPostEventTakeCreation)
    disconnectSignal('previewanimationsettingschanged', SkeletalAnimationEventManager_onPreviewAnimationSettingsChanged)
    disconnectSignal('renderassetloaded', SkeletalAnimationEventManager_onRenderAssetLoaded)


# This function clears the current skeletal animation tree and builds a new one
# from the information stored in the take corresponding to the specified
# animation.
def _buildSkeletalAnimationTree(groupName, animName):
    if isActorLoaded() and len(getRenderAssetName()) > 0 and isRenderAssetValid() and renderAssetHasSkeletalAnimationTree() and len(groupName) > 0 and len(animName) > 0:
        disabledUndo = False
        try:
            eventTake = EventTake(groupName, animName)
            # Temporarily disable the undo/redo system. This is because this is called inside a Python signal
            # so these commands will be listed in the undo/redo stacks on *top* of the command that triggered
            # the signal. Since we build the tree based on data already present when the signal is fired it is
            # actually an error that these commands end up on the undo/redo stacks anyway.
            issueCommand('undo -disable')
            disabledUndo = True
            issueCommand('animtree -clear')
            for event in eventTake.events:
                payload = string.strip(event.customPayload)
                match = re.match('game:\s+playanim\s+\w+', payload)
                if match != None:
                    skeletalAnimationName = re.split(r'\W+', match.group())[2]
                    issueCommand('animtree -silent -add -animation {0} -starttime {1} -blendintime {2} -blendouttime {3} -durationscale {4} -magnitudescale {5}'.format(skeletalAnimationName, event.startTime, event.blendInTime, event.blendOutTime, event.durationScale, event.magnitudeScale))
            issueCommand('undo -enable')
        except Exception, e:
            if disabledUndo:
                issueCommand('undo -enable')
            raise FaceFXError('{0}'.format(e))


# Checks for animation bounds intersections between the preview animation and the animation tree.
def _checkForPreviewAnimationIntersection():
    previewAnimSettings = PreviewAnimationSettings()
    if previewAnimSettings.animationName != None:
        endTime = previewAnimSettings.startTime + previewAnimSettings.length
        if previewAnimSettings.loop == True:
            # 365.25 days is 31,557,600 seconds which should be for all intents and purposes an infinite end time when looping.
            endTime = 31557600.0
        duplicateInRange = next((anim for anim in getSkeletalAnimationTreeAnimsInTimeRange(previewAnimSettings.startTime, endTime) if anim[0] == previewAnimSettings.animationName), None)
        if duplicateInRange != None:
            # This command should be on the undo/redo stacks just to preserve state but note that when this happens getting
            # back to the previous state will now require two undos instead of one.
            issueCommand('previewanim -animation ""')
            warn('Disabled preview animation {0} because it overlaps the same animation with start time {1} in the skeletal animation events tree!'.format(previewAnimSettings.animationName, duplicateInRange[1]))


# When the animation selection changes we need to build a new skeletal animation tree.
def SkeletalAnimationEventManager_onAnimationChanged(groupName, animName):
    _buildSkeletalAnimationTree(groupName, animName)
    _checkForPreviewAnimationIntersection()


# When a new take is created we need to build a new skeletal animation tree.
def SkeletalAnimationEventManager_onPostEventTakeCreation(groupName, animName):
    _buildSkeletalAnimationTree(groupName, animName)
    _checkForPreviewAnimationIntersection()


# When the preview animation settings change we need to check for preview animation intersections.
def SkeletalAnimationEventManager_onPreviewAnimationSettingsChanged():
    _checkForPreviewAnimationIntersection()


# When the user changes the render asset we need to build a new skeletal animation tree.
def SkeletalAnimationEventManager_onRenderAssetLoaded():
    _buildSkeletalAnimationTree(getSelectedAnimGroupName(), getSelectedAnimName())
    _checkForPreviewAnimationIntersection()
