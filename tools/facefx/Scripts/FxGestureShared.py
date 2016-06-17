#-------------------------------------------------------------------------------
# Some useful classes for generating events, animations, and curves from script.
#
# Owner: Doug Perkowski
#
# Copyright (c) 2002-2012 OC3 Entertainment, Inc.
#-------------------------------------------------------------------------------
from FxStudio import *


def getScriptSetting(cvarName, defaultValue):
    retVal = getConsoleVariableImpl(cvarName)
    if None == retVal:
        retVal = defaultValue
        echo("setting console variable " + cvarName + " to " + str(retVal))
    return retVal


class Key:
    def __init__(self, time, value, slopein=0, slopeout=0):
        self.time = time
        self.value = value
        self.slopein = slopein
        self.slopeout = slopeout


class Curve:
    def __init__(self, name):
        self.name = name
        self.keys = []


# A special constructor for a curve that is one second long, a useful construct for
# Events with sticky values.
class OneSecondCurve:
    def __init__(self, name, value):
        self.name = name
        self.keys = [Key(0, value), Key(1, value)]


class Anim:
    def __init__(self, name, group):
        self.group = group
        self.name = name
        self.curves = []
        self.events = []
        self.groupChildEvents = "false"
        issueCommand('anim -add -group "%s" -name "%s";' % (self.group, self.name))

    #Nothing Happens until you build the animation with this function.
    def buildAnim(self):
        issueCommand('select -type "animgroup" -names "%s";' % (self.group))
        issueCommand('select -type "anim" -names "%s";' % (self.name))
        for curve in self.curves:
            issueCommand('curve -group "%s" -anim "%s" -add -name "%s" -owner "user";' % (self.group, self.name, curve.name))
            issueCommand('select -type "anim" -names "%s";' % (self.name))
            issueCommand('select -type "curve" -names "%s";' % (curve.name))
            for key in curve.keys:
                issueCommand('key -insert -default -time "%s" -value "%s";' % (key.time, key.value))
        for event in self.events:
            if self.groupChildEvents == "false":
                issueCommand('event -group "%s" -anim "%s" -add -eventgroup "%s" -eventanim "%s" -persist "%s" -inheritmag "%s" -inheritdur "%s" -probability "%f" -minstart "%f" -maxstart "%f" -minduration "%f" -maxduration "%f" -minmagnitude "%f" -maxmagnitude "%f" -minblendin "%f" -maxblendin "%f" -minblendout "%f" -maxblendout "%f" -blendunscaled "%s" -useparentblend "%s";' % (self.group, self.name, event.group, event.name, event.persist, event.inheritmag, event.inheritdur, event.probability, event.minstart, event.maxstart, event.minduration, event.maxduration, event.minmagnitude, event.maxmagnitude, event.minblendin, event.maxblendin, event.minblendout, event.maxblendout, event.blendunscaled, event.useparentblend))
            if self.groupChildEvents != "false":
                issueCommand('event -group "%s" -anim "%s" -add -eventgroup "%s" -eventanim "%s" -persist "%s" -inheritmag "%s" -inheritdur "%s" -weight "%f" -probability "%f" -minstart "%f" -maxstart "%f" -minduration "%f" -maxduration "%f" -minmagnitude "%f" -maxmagnitude "%f" -minblendin "%f" -maxblendin "%f" -minblendout "%f" -maxblendout "%f" -blendunscaled "%s" -useparentblend "%s";' % (self.group, self.name, event.group, event.name, event.persist, event.inheritmag, event.inheritdur, event.weight, event.probability, event.minstart, event.maxstart, event.minduration, event.maxduration, event.minmagnitude, event.maxmagnitude, event.minblendin, event.maxblendin, event.minblendout, event.maxblendout, event.blendunscaled, event.useparentblend))


class Event:
    def __init__(self, animName, animGroup, durationScale=1, magnitudeScale=1):
        self.name = animName
        self.group = animGroup
        self.probability = 1
        self.minstart = 0
        self.maxstart = 0
        self.minduration = durationScale
        self.maxduration = durationScale
        self.minmagnitude = magnitudeScale
        self.maxmagnitude = magnitudeScale
        self.minblendin = 0
        self.maxblendin = 0
        self.minblendout = 0
        self.maxblendout = 0
        self.weight = 1
        # must be set to "true" or "false"
        self.persist = "false"
        self.inheritmag = "true"
        self.inheritdur = "true"
        self.blendunscaled = "false"
        self.useparentblend = "false"

    def set_start(self, start):
        self.minstart = start
        self.maxstart = start

    def set_duration(self, duration):
        self.minduration = duration
        self.maxduration = duration

    def set_magnitude(self, magnitude):
        self.minmagnitude = magnitude
        self.maxmagnitude = magnitude

    def set_blendin(self, blendin):
        self.minblendin = blendin
        self.maxblendin = blendin

    def set_blendout(self, blendout):
        self.minblendout = blendout
        self.maxblendout = blendout
