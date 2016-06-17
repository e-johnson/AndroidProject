""" This module provides Python wrappers around animation code.

classes:

Key -- A single key in an animation curve.
Curve -- A collection of keys that can be evaluated at a certain time.
ChildEvent -- A single event in the event template.
ChildEventGroup -- A group of child events, from which only one can spawn.
EventTemplate -- The collection of child event groups which produces the Take.
Animation -- A collection of curves and an event template. A wrapper around a
    FaceFx Studio animation.
PreviewAnimationSettings - The preview animation settings for the currently
    selected animation in FaceFX Studio.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import getEventTemplate, getEventTake, getAnimationProperties,\
    getCurveNames, getKeys, isCurveOwnedByAnalysis,\
    getPreviewAnimationSettings, FaceFXError, getSelectedAnimName,\
    getSelectedAnimGroupName
from FxPhonemes import PhonemeWordList


class Key(object):
    """ A wrapper around a single key.

    instance variables:

    time -- The time of the key, in seconds.
    value -- The value of the key
    slopeIn -- The slope of the curve as it comes into the key
    slopeOut -- The slope of the curve as it leaves the key

    """

    def __init__(self, keyTupleFromStudio):
        """ Initializes the key from a tuple sent back from FaceFx Studio.

        parameters:

        keyTupleFromStudio -- A tuple (time, value, slopeIn, slopeOut)

        """
        self.time = keyTupleFromStudio[0]
        self.value = keyTupleFromStudio[1]
        self.slopeIn = keyTupleFromStudio[2]
        self.slopeOut = keyTupleFromStudio[3]

    def __str__(self):
        """ Returns the string representation of the key. """
        return 'Key: time={0}, value={1}, slopeIn={2}, slopeOut={3}'.format(
            self.time, self.value, self.slopeIn, self.slopeOut)

    def __repr__(self):
        """ Returns the Python represenation of the key. """
        return 'Key(({0}, {1}, {2}, {3}))'.format(self.time, self.value,
            self.slopeIn, self.slopeOut)


class HermiteKeyInterpolator(object):
    """ A class that performs a modified Hermite interpolation between two keys.

    """

    def interpolate(self, firstKey, secondKey, time):
        """ Perform a modified Hermite interpolation between two keys.
        Returns the curve value at the requested time between the keys.

        keyword arguments:

        firstKey -- the key with a time less than "time"
        secondKey -- the key with a time greater than "time"
        time -- the time for which to evaluate.

        returns: float

        """
        time1 = firstKey.time
        time2 = secondKey.time
        deltaTime = time2 - time1
        parametricTime = (time - time1) / deltaTime

        p0 = firstKey.value
        p1 = secondKey.value
        m0 = firstKey.slopeOut * deltaTime
        m1 = secondKey.slopeIn * deltaTime

        return parametricTime * (parametricTime * (parametricTime *
            (2.0 * p0 - 2.0 * p1 + m0 + m1) +
            (-3.0 * p0 + 3.0 * p1 - 2.0 * m0 - m1)) +
            m0) + p0


class Curve(object):
    """ A collection of keys that can be evaluated at a given time.

    instance variables:

    animation -- a reference back to the animation containing this curve
    name -- the name of the curve
    interpolator -- an object that can interpolate(firstKey, secondKey, time)
    keys -- a list of the keys in the animation
    isOwnedByAnalysis -- boolean; True if the curve is owned by analysis,
        meaning changes cannot be brought back into FaceFX Studio

    """

    def __init__(self, name, curveTupleFromStudio, animation):
        """ Initializes the animation with the tuple from studio. """
        self.animation = animation
        self.name = name
        self.interpolator = HermiteKeyInterpolator()
        self.keys = [Key(key) for key in curveTupleFromStudio]
        self.isOwnedByAnalysis = isCurveOwnedByAnalysis(
            self.animation.groupName, self.animation.name, self.name)

    def __str__(self):
        """ Returns the string representation of the curve. """
        return 'Curve: "{0}" [{1} keys, owned by {2}]'.format(
            self.name, len(self),
            'Analysis' if self.isOwnedByAnalysis else 'User')

    def __repr__(self):
        """ Hackish repr to make printing lists of curves pretty. """
        return self.__str__()

    def __len__(self):
        """ Returns the number of keys in the curve. """
        return len(self.keys)

    def __getitem__(self, item):
        """ Returns the key at item. """
        return self.keys[item]

    def getInterpolator(self):
        """ Returns the interpolator object in use by the curve. """
        return self.interpolator

    def setInterpolator(self, interpolator):
        """ Sets the interpolator object that the curve will use to evaluate """
        self.interpolator = interpolator

    def getNumKeys(self):
        """ Returns the number of keys in the curve """
        return len(self)

    def getStartTime(self):
        """ Returns the time of the first key. """
        try:
            return self[0].time
        except IndexError:
            return 0.0

    def getEndTime(self):
        """ Returns the time of the last key. """
        try:
            return self[-1].time
        except IndexError:
            return 0.0

    def evaluateAt(self, time):
        """ Evaluates the curve at the given time.

        keyword arguments:

        time -- the time in seconds to evaluate at

        """
        value = 0.0
        numKeys = self.getNumKeys()
        if numKeys > 0:
            numKeysM1 = numKeys - 1
            # Check for out-of-range time and clamp to end points of curve.
            if time <= self.keys[0].time:
                value = self.keys[0].value
            elif time >= self.keys[numKeysM1].time:
                value = self.keys[numKeysM1].value
            else:
                # The time is in range.
                if 1 == numKeys:
                    value = self.keys[0].value
                else:
                    # Find the bounding keys.
                    firstKey = 0
                    secondKey = 0
                    pos = 0
                    for i in range(numKeysM1):
                        if self.keys[i].time <= time and time < self.keys[i + 1].time:
                            pos = i
                            break
                    if pos != numKeysM1:
                        firstKey = pos
                        secondKey = pos + 1
                    else:
                        firstKey = pos - 1
                        secondKey = pos
                    # Interpolate.
                    value = self.interpolator.interpolate(self.keys[firstKey], self.keys[secondKey], time)
        return value


class ChildEvent(object):
    """ A wrapper around a child event in the event template.

    instance variables:

    animGroupName -- the name of the animation group the event points to
    animName -- the name of the animation the event points to
    startTimeRange -- a tuple defining the range when the event can start
    magnitudeRange -- a tuple defining the range of the event's magnitude scale
    durationRange -- a tuple defining the range of the event's duration scale
    blendInRange -- a tuple defining the range of the event's blend in time
    blendOutRange -- a tuple defining the range of the event's blend out time
    customPayload -- a string that will be sent back to the game engine at the
        event's ingress when the event is played in game
    eventID -- a read-only internal identifier
    isDurationScaledByParent -- If this is true then when the take is created
        this event's duration will be scaled by the duration scale of the
        event that spawned it into the take. If this is false or this event
        was not spawned by another event this event's duration will fall within
        its own durationRange.
    isMagnitudeScaledByParent -- If this is true then when the take is created
        this event's magnitude will be scaled by the magnitude scale of the
        event that spawned it into the take. If this is false or this event
        was not spawned by another event this event's magnitude will fall within
        its own magnitudeRange.
    isBlendUnscaled -- True if the event's blend times are unscaled by the
        event's duration
    useParentBlendTimes -- True if the event's blend times where inherited from
        the event that spawned it into the take.
    shouldPersistValue -- True if the event's values will "stick" on the
        character at the event's egress
    spawnConditionProbability -- The probability that the event will be spawned
        into the take. A value of None or 1.0 means it is always spawned.
    spawnConditionDurationScale -- If the duration scale of the event that
        could possibly spawn this event into the take falls into this range then
        this event will be spawned. A value of None means it is unbounded to
        that side.
    spawnConditionMagnitudeScale -- If the magnitude scale of the event that
        could possibly spawn this event into the take falls into this range then
        this event will be spawned. A value of None means it is unbounded to
        that side.
    spawnConditionStartTimeOffset -- If the actual start time of the event that
        could possibly spawn this event into the take falls into this range this
        event will be spawned. A value of None means it is unbounded to
        that side.
    weight -- The weight assigned to this event in a group, used for picking
        one event from a group of child events

    """

    def __init__(self, childEventTupleFromStudio):
        """ Initializes the child event with the tuple from Studio. """
        self.animGroupName = childEventTupleFromStudio[0]
        self.animName = childEventTupleFromStudio[1]
        self.startTimeRange = childEventTupleFromStudio[2]
        self.magnitudeRange = childEventTupleFromStudio[3]
        self.durationRange = childEventTupleFromStudio[4]
        self.blendInRange = childEventTupleFromStudio[5]
        self.blendOutRange = childEventTupleFromStudio[6]
        self.customPayload = childEventTupleFromStudio[7]
        self.eventID = childEventTupleFromStudio[8]
        self.isDurationScaledByParent = childEventTupleFromStudio[9]
        self.isMagnitudeScaledByParent = childEventTupleFromStudio[10]
        self.isBlendUnscaled = childEventTupleFromStudio[11]
        self.useParentBlendTimes = childEventTupleFromStudio[12]
        self.shouldPersistValues = childEventTupleFromStudio[13]
        self.spawnConditionProbability = childEventTupleFromStudio[14]
        self.spawnConditionDurationScale = childEventTupleFromStudio[15]
        self.spawnConditionMagnitudeScale = childEventTupleFromStudio[16]
        self.spawnConditionStartTimeOffset = childEventTupleFromStudio[17]
        self.weight = childEventTupleFromStudio[18]

    def __str__(self):
        """ Returns the string representation of the child event. """
        r = "animGroupName: " + str(self.animGroupName) + "\n"
        r += "animName: " + str(self.animName) + "\n"
        r += "startTimeRange: (" + str(self.startTimeRange[0]) + ", " + str(self.startTimeRange[1]) + ")" + "\n"
        r += "magnitudeRange: (" + str(self.magnitudeRange[0]) + ", " + str(self.magnitudeRange[1]) + ")" + "\n"
        r += "durationRange: (" + str(self.durationRange[0]) + ", " + str(self.durationRange[1]) + ")" + "\n"
        r += "blendInRange: (" + str(self.blendInRange[0]) + ", " + str(self.blendInRange[1]) + ")" + "\n"
        r += "blendOutRange: (" + str(self.blendOutRange[0]) + ", " + str(self.blendOutRange[1]) + ")" + "\n"
        r += "customPayload: " + str(self.customPayload) + "\n"
        r += "eventID: " + str(self.eventID) + "\n"
        r += "isDurationScaledByParent: " + str(self.isDurationScaledByParent) + "\n"
        r += "isMagnitudeScaledByParent: " + str(self.isMagnitudeScaledByParent) + "\n"
        r += "isBlendUnscaled: " + str(self.isBlendUnscaled) + "\n"
        r += "useParentBlendTimes: " + str(self.useParentBlendTimes) + "\n"
        r += "shouldPersistValues: " + str(self.shouldPersistValues) + "\n"
        r += "spawnConditionProbability: " + str(self.spawnConditionProbability) + "\n"
        r += "spawnConditionDurationScale: (" + str(self.spawnConditionDurationScale[0]) + ", " + str(self.spawnConditionDurationScale[1]) + ")" + "\n"
        r += "spawnConditionMagnitudeScale: (" + str(self.spawnConditionMagnitudeScale[0]) + ", " + str(self.spawnConditionMagnitudeScale[1]) + ")" + "\n"
        r += "spawnConditionStartTimeOffset: (" + str(self.spawnConditionStartTimeOffset[0]) + ", " + str(self.spawnConditionStartTimeOffset[1]) + ")" + "\n"
        r += "weight: " + str(self.weight) + "\n"
        return r


class ChildEventGroup(object):
    """ A group of child events.

    instance variables:

    childEvents -- a list of the child events in the group

    """

    def __init__(self, childEventGroupTupleFromStudio):
        """ Initializes the child event group with the tuple from Studio. """
        self.childEvents = [ChildEvent(e) for e in
            childEventGroupTupleFromStudio]

    def __len__(self):
        """ Returns the number of child events in the group. """
        return len(self.childEvents)

    def __getitem__(self, item):
        """ Returns the child event at item """
        return self.childEvents[item]

    def getNumChildEvents(self):
        """ Returns the number of child events in the group. """
        return len(self)

    def __str__(self):
        """ Returns the string representation of the child event group. """
        r = str(self.getNumChildEvents()) + " childEvents:\n"
        childEventIndex = 0
        for childEvent in self.childEvents:
            r += "childEvent " + str(childEventIndex) + ":\n"
            r += str(childEvent)
            childEventIndex += 1
        return r


class EventTemplate(object):
    """ An event template defines the events that might be spawned in a take.

    instance variables:

    templateRevisionID -- a read-only internal identifier
    childEventGroups -- a list of the groups of child events in the template

    """

    def __init__(self, animGroupName, animName):
        """ Requests the event template for the given animation from Studio. """
        eventTemplateTuple = getEventTemplate(animGroupName, animName)
        self.templateRevisionID = -1
        self.childEventGroups = []
        if len(eventTemplateTuple) >= 2:
            self.templateRevisionID = eventTemplateTuple[0]
            for childEventGroup in eventTemplateTuple[1]:
                self.childEventGroups.append(ChildEventGroup(childEventGroup))

    def __len__(self):
        """ Returns the number of child event groups in the template. """
        return len(self.childEventGroups)

    def __getitem__(self, item):
        """ Returns the child event group at item. """
        return self.childEventGroups[item]

    def getNumChildEventGroups(self):
        """ Returns the number of child event groups in the template. """
        return len(self.childEventGroups)

    def __str__(self):
        """ Returns the string representation of the event template. """
        r = "templateRevisionID: " + str(self.templateRevisionID) + "\n"
        r += str(self.getNumChildEventGroups()) + " childEventGroups:\n"
        childEventGroupIndex = 0
        for childEventGroup in self.childEventGroups:
            r += "childEventGroup " + str(childEventGroupIndex) + ":\n"
            r += str(childEventGroup)
            childEventGroupIndex += 1
        return r


class Event(object):
    """ An event contained in a take.

    instance variables:

    animGroupName -- the name of the animation group the event points to
    animName -- the name of the animation the event points to
    startTime -- the start time of the event (in seconds)
    duration -- the duration of the event (in seconds)
    durationScale -- the duration scale of the event
    magnitudeScale -- the magnitude scale of the event
    blendInTime -- the blend in time of the event (in seconds)
    blendOutTime -- the blend out time of the event (in seconds)
    shouldPersistValue -- True if the event's values will "stick" on the
        character at the event's egress
    customPayload -- a string that will be sent back to the game engine at the
        event's ingress when the event is played in game
    eventID -- a read-only internal identifier

    """

    def __init__(self, eventTupleFromStudio):
        """ Initializes the event with the tuple from Studio. """
        self.animGroupName = eventTupleFromStudio[0]
        self.animName = eventTupleFromStudio[1]
        self.startTime = eventTupleFromStudio[2]
        self.duration = eventTupleFromStudio[3]
        self.durationScale = eventTupleFromStudio[4]
        self.magnitudeScale = eventTupleFromStudio[5]
        self.blendInTime = eventTupleFromStudio[6]
        self.blendOutTime = eventTupleFromStudio[7]
        self.shouldPersistValues = eventTupleFromStudio[8]
        self.customPayload = eventTupleFromStudio[9]
        self.eventID = eventTupleFromStudio[10]

    def __str__(self):
        """ Returns the string representation of the event. """
        r = "animGroupName: " + str(self.animGroupName) + "\n"
        r += "animName: " + str(self.animName) + "\n"
        r += "startTime: " + str(self.startTime) + "\n"
        r += "duration: " + str(self.duration) + "\n"
        r += "durationScale: " + str(self.durationScale) + "\n"
        r += "magnitudeScale: " + str(self.magnitudeScale) + "\n"
        r += "blendInTime: " + str(self.blendInTime) + "\n"
        r += "blendOutTime: " + str(self.blendOutTime) + "\n"
        r += "shouldPersistValues: " + str(self.shouldPersistValues) + "\n"
        r += "customPayload: " + str(self.customPayload) + "\n"
        r += "eventID: " + str(self.eventID) + "\n"
        return r


class EventTake(object):
    """ An event take defines the events that are actually in the take.

    instance variables:

    events -- a list of the events contained in the take

    """

    def __init__(self, animGroupName, animName):
        """ Requests the event take for the given animation from Studio. """
        eventTakeTuple = getEventTake(animGroupName, animName)
        self.events = []
        for event in eventTakeTuple:
            self.events.append(Event(event))

    def __len__(self):
        """ Returns the number of events in the take. """
        return len(self.events)

    def __getitem__(self, item):
        """ Returns the event at item. """
        return self.events[item]

    def getNumEvents(self):
        """ Returns the number of events in the take. """
        return len(self.events)

    def __str__(self):
        """ Returns the string representation of the event take. """
        r = str(self.getNumEvents()) + " events:\n"
        eventIndex = 0
        for event in self.events:
            r += "event " + str(eventIndex) + ":\n"
            r += str(event)
            eventIndex += 1
        return r


class Animation(object):
    """ A collection of curves, an event template, an event take, and other
    animation properties.

    instance variables:

    groupName -- the name of the group containing the animation
    name -- the name of the animation
    startTime -- the start time of the animation, either events or curves
    endTime -- the end time of the animation, either events or curves
    curvesStartTime -- the start time of the curves
    curvesEndTime -- the end time of the curves
    frameRate -- the frame rate of the animation
    absoluteAudioAssetPath -- the absolute path to the audio asset
    audioAssetPath -- the relative path to the audio asset
    language -- the language the animation was analyzed in
    analysisActor -- the name of the analysis actor used to analyze the anim
    analysisText -- the text used to analyze the anim
    confidence -- the confidence score from analysis.
    phonemeWordList -- a PhonemeWordList object containing the phonemes and
        words that were output by the analysis
    curves -- a list of Curve objects containing the curves in the animation
    eventTemplate -- an EventTemplate object containing the child event groups
    eventTake -- an EventTake object containing the events

    """

    def __init__(self, animGroupName, animName):
        """ Initializes the animation by pulling the data from Studio. """
        self.groupName = animGroupName
        self.name = animName
        self.path = animGroupName + "/" + animName
        try:
            animationProperties = getAnimationProperties(animGroupName, animName)
            self.startTime = animationProperties[0]
            self.endTime = animationProperties[1]
            self.curvesStartTime = animationProperties[2]
            self.curvesEndTime = animationProperties[3]
            self.frameRate = animationProperties[4]
            self.absoluteAudioAssetPath = animationProperties[5]
            self.audioAssetPath = animationProperties[6]
            self.language = animationProperties[7]
            self.analysisActor = animationProperties[8]
            self.analysisText = animationProperties[9]
            self.confidence = animationProperties[10]
            self.phonemeWordList = PhonemeWordList(animGroupName, animName)
            curveNames = getCurveNames(animGroupName, animName)
            self.curves = [Curve(c, getKeys(animGroupName, animName, c), self)
                for c in curveNames]
            self.eventTemplate = EventTemplate(animGroupName, animName)
            self.eventTake = EventTake(animGroupName, animName)
        except Exception, e:
            raise FaceFXError('{0}'.format(e))

    def getNumCurves(self):
        """ Returns the number of curves in the animation. """
        return len(self.curves)

    def findCurve(self, curveName):
        """ Returns the curve with the requested name, or None. """
        for curve in self.curves:
            if curve.name == curveName:
                return curve
        return None

    def __str__(self):
        """ Returns the string representation of the Animation. """
        r = str(self.path) + ":\n"
        r += "        startTime: " + str(self.startTime) + "\n"
        r += "        endTime: " + str(self.endTime) + "\n"
        r += "        curvesStartTime: " + str(self.curvesStartTime) + "\n"
        r += "        curvesEndTime: " + str(self.curvesEndTime) + "\n"
        r += "        frameRate: " + str(self.frameRate) + "\n"
        r += "        absoluteAudioAssetPath: " + self.absoluteAudioAssetPath + "\n"
        r += "        audioAssetPath: " + self.audioAssetPath + "\n"
        r += "        language: " + self.language + "\n"
        r += "        confidence: " + str(self.confidence) + "\n"
        r += "        analysisActor: " + self.analysisActor + "\n"
        r += "        analysisText: " + self.analysisText + "\n"
        r += "        " + str(self.getNumCurves()) + " curves:\n"
        curveIndex = 0
        for curve in self.curves:
            r += "                [" + str(curveIndex) + "] " + str(curve) + "\n"
            curveIndex += 1
        return r


class PreviewAnimationSettings(object):
    """ The preview animation settings for the currently selected animation in
        FaceFX Studio.

    instance variables:

    blendMode -- the current preview animation blend mode
    animationName -- the name of the skeletal animation being used for preview
        purposes
    length -- the length of the preview animation (in seconds)
    startTime -- the time at which the preview animation starts in the FaceFX
        Studio timeline (in seconds)
    blendInTime -- the time (in seconds) over which the preview animation blends
        in
    blendOutTime -- the time (in seconds) over which the preview animation
        blends out
    loop - inidcates whether or not the preview animation is looping

    Notes: blendMode is always valid (a string), but the other instance
        variables will be set to None if there is no preview animation
        selected in FaceFX Studio

    """

    def __init__(self):
        """ Initializes the preview animation settings with the tuple from Studio. """
        previewAnimationSettingsTupleFromStudio = getPreviewAnimationSettings()
        self.blendMode = previewAnimationSettingsTupleFromStudio[0]
        if "" == previewAnimationSettingsTupleFromStudio[1]:
            self.animationName = None
            self.length = None
            self.startTime = None
            self.blendInTime = None
            self.blendOutTime = None
            self.loop = None
        else:
            self.animationName = previewAnimationSettingsTupleFromStudio[1]
            self.length = previewAnimationSettingsTupleFromStudio[2]
            self.startTime = previewAnimationSettingsTupleFromStudio[3]
            self.blendInTime = previewAnimationSettingsTupleFromStudio[4]
            self.blendOutTime = previewAnimationSettingsTupleFromStudio[5]
            self.loop = previewAnimationSettingsTupleFromStudio[6]

    def __str__(self):
        """ Returns the string representation of the preview animation settings. """
        r = "Preview Animation Settings:\n"
        r += "        blendMode: " + str(self.blendMode) + "\n"
        r += "        animationName: " + str(self.animationName) + "\n"
        r += "        length: " + str(self.length) + "\n"
        r += "        startTime: " + str(self.startTime) + "\n"
        r += "        blendInTime: " + str(self.blendInTime) + "\n"
        r += "        blendOutTime: " + str(self.blendOutTime) + "\n"
        r += "        loop: " + str(self.loop) + "\n"
        return r


def get_selected_animation():
    """ Returns the currently selected animation. Returns None if no animation
    was selected. """
    group_name = getSelectedAnimGroupName()
    anim_name = getSelectedAnimName()
    try:
        return Animation(group_name, anim_name)
    except FaceFXError:
        return None
