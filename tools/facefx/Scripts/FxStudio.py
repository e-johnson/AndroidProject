""" FaceFX Studio Python Scripting Interface.

This module provides read access to a multitude of information about the current
actor loaded in FaceFX Studio. The module also provides a wrapper around
executing FaceFX commands, to get data back into FaceFX Studio once it has been
modified in Python.

related modules:

FxAnimation -- provides wrappers around animation data from Studio
FxAudio -- provides a wrapper around the selected audio in Studio
FxFaceGraph -- provides wrappers around Face Graph data from Studio
FxPhonemes -- provides wrappers around phoneme data from Studio
FxRandom -- provides random number generating functions
FxUtil -- provides a few utility functions

classes:

FaceFXError -- The error produced if any function fails in the FxStudio module.
FaceFXDeprecatedWarning -- The warning produced if any function in FaceFX modules is deprecated.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os
from FxStudio import *


class FaceFXError(Exception):
    """ The error produced if any function fails in the FxStudio module.

    instance variables:

    message - a human-readable description of what went wrong.

    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class FaceFXDeprecatedWarning(DeprecationWarning):
    """ The warning produced if any function in FaceFX modules is deprecated.

    instance variables:

    message - a human-readable description of what went wrong.

    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


#-------------------------------------------------------------------------------
# These functions issue commands to FaceFX Studio but use a cleaner and easier
# to use syntax than calling FxStudio.issueCommand() directly.
#-------------------------------------------------------------------------------

def echo(msg):
    """ Deprecated, but here for compatibility with old scripts. Use msg() instead."""
    if not issueCommand('print -message "{0}"'.format(msg)):
        raise FaceFXError('FxStudio.echo() failed!')


# Note that there is also a Unicode version: FxStudio.msgW().
def msg(msg):
    """ Print msg to FaceFX Studio's console."""
    if not issueCommand('print -message "{0}"'.format(msg)):
        raise FaceFXError('FxStudio.msg() failed!')


# Note that there is also a Unicode version: FxStudio.warnW().
def warn(msg):
    """ Print msg to FaceFX Studio's console (as a warning)."""
    if not issueCommand('warn -message "{0}"'.format(msg)):
        raise FaceFXError('FxStudio.warn() failed!')


# Note that there is also a Unicode version: FxStudio.errorW().
def error(msg):
    """ Print msg to FaceFX Studio's console (as an error)."""
    if not issueCommand('error -message "{0}"'.format(msg)):
        raise FaceFXError('FxStudio.error() failed!')


# Note that there is also a Unicode version: FxStudio.devW().
def dev(msg):
    """ Print msg to FaceFX Studio's developer console (as a developer trace). Note that the developer console is only visible in special developer builds."""
    if not issueCommand('dev -message "{0}"'.format(msg)):
        raise FaceFXError('FxStudio.dev() failed!')


def msgBox(msg):
    """ Displays an informational message box in FaceFX Studio or prints a message in command line mode."""
    displayMessageBox(msg, 'info')


def warnBox(msg):
    """ Displays a warning message box in FaceFX Studio or prints a message in command line mode."""
    displayMessageBox(msg, 'warning')


def errorBox(msg):
    """ Displays an error message box in FaceFX Studio or prints a message in command line mode."""
    displayMessageBox(msg, 'error')


def setConsoleVariable(cvarName, cvarValue):
    """ Sets (or creates) a console variable in FaceFX Studio.

    If the variable does not exist, it is created. Console variables can be
    queried for their current value by using FxStudio.getConsoleVariable(cvar),
    which will return a string with the current value or None if the variable
    does not exist. Note that the default value of the console variable can be
    queried by using FxStudio.getConsoleVariableDefault(cvar) which behaves
    exactly like FxStudio.getConsoleVariable().

    FxUtil.isConsoleVariableSetToDefault() is a convenient helper method.

    keywordArguments:

    cvarName -- the name of the console variable
    cvarValue -- the value of the console variable

    """
    if None == getConsoleVariableImpl(cvarName):
        print 'cvar {0} does not exist and will be created automatically with the value {1}'.format(cvarName, cvarValue)
    retCode = issueCommand('set -name "{0}" -value "{1}"'.format(
        cvarName, cvarValue))
    if False == retCode:
        raise FaceFXError('Console variable {0} could not be created.'.format(
            cvarName))


def setConsoleVariableFast(cvarName, cvarValue):
    """ Sets a console variable in FaceFX Studio without any error checking or
    command execution.

    Useful for progress display console variables or when you know the console
    variable exists and don't want to issue a command through the command system
    to set it.

    keywordArguments:

    cvarName -- the name of the console variable
    cvarValue -- the value of the console variable

    """
    setConsoleVariableFastImpl(cvarName, str(cvarValue))


def getConsoleVariable(cvarName):
    """ Returns a console variable value in FaceFX Studio.

    If the console variable does not exist, a FaceFXError is raised.
    """
    retVal = getConsoleVariableImpl(cvarName)
    if None == retVal:
        raise FaceFXError('cvar {0} does not exist.'.format(cvarName))
    return retVal


def getConsoleVariableDefault(cvarName):
    """Returns a console variable default value in FaceFX Studio.

    If the console variable does not exist, a FaceFXError is raised.
    """
    retVal = getConsoleVariableDefaultImpl(cvarName)
    if None == retVal:
        raise FaceFXError('cvar {0} does not exist.'.format(cvarName))
    return retVal


def getConsoleVariableAsSwitch(cvarName):
    """Returns a console variable value as a switch value. Returns True
    if the switch is enabled and False if it is not.

    If the console variable does not exist, a FaceFXError is raised.
    """
    retVal = getConsoleVariableAsSwitchImpl(cvarName)
    if None == retVal:
        raise FaceFXError('cvar {0} does not exist.'.format(cvarName))
    return retVal


def getDirectory(dir):
    """Returns the specified directory."""
    varmap = {'app': 'g_appdirectory',
              'clientspec_root': 'g_clientspecroot',
              'user': 'g_userdirectory',
              'settings': 'g_settingsdirectory',
              'logs': 'g_logsdirectory',
              'templates': 'g_templatesdirectory'}
    try:
        return getConsoleVariable(varmap[dir.lower()])
    except(KeyError):
        raise FaceFXError('{0} is not a valid directory for FxStudio.getDirectory()'.format(dir))


def getSearchPath(searchPath):
    """Returns the specified search path as a list of Unicode strings.
    If the search path is a search path that FaceFX Studio knows about, the full search path is returned.
    Otherwise if the search path exists in the current clientspec file the clientspec entry is returned.

    If the search path does not exist, a FaceFXError is raised.
    """
    retVal = getSearchPathImpl(searchPath)
    if None == retVal:
        raise FaceFXError('searchPath {0} does not exist.'.format(searchPath))
    return retVal


def getLogFileFullPath(baseName):
    """Returns the full path to a fully constructed log file, correctly named
    and formatted.
    """
    return os.path.normpath(''.join([getDirectory('logs'),
        createLogFileName(baseName)]))


def getSDKVersion():
    """Returns the FaceFX SDK version."""
    return getConsoleVariable("g_sdkversion")


def getLicenseeName():
    """Returns the licensee name."""
    return getConsoleVariable("g_licenseename")


def getLicenseeProjectName():
    """Returns the licensee project name."""
    return getConsoleVariable("g_licenseeprojectname")


def getAppIconPath():
    """Returns the application icon path."""
    return getDirectory('app') + 'res\\FxStudioApp.ico'


# Creates a new FaceFX Actor in FaceFX Studio.
def createNewActor(actorName):
    """ Creates a new FaceFX Actor in FaceFX Studio.

    keyword arguments:

    actorName -- the desired name for the actor.
    """
    if not issueCommand('newActor -name "{0}"'.format(actorName)):
        raise FaceFXError('Actor could not be created.')


def loadActor(actorFile):
    """ Loads the specified .facefx file (FaceFX Actor) into FaceFX Studio. """
    if not issueCommand('loadActor -file "{0}"'.format(actorFile)):
        raise FaceFXError('Actor in file {0} could not be loaded'.format(
            actorFile))


def closeActor():
    """Closes the currently loaded .facefx file (FaceFX Actor) in FaceFX Studio.
    """
    if not issueCommand("closeActor"):
        raise FaceFXError('Actor could not be closed.')


def saveActor(actorFile):
    """Saves the currently loaded .facefx file (FaceFX Actor) in FaceFX Studio.
    """
    if not issueCommand('saveActor -file "{0}"'.format(actorFile)):
        raise FaceFXError('Could not save actor to {0}'.format(actorFile))


def selectAnimation(groupName, animName):
    """Selects the specified animation in the actor loaded in FaceFX Studio

    keyword arguments:

    groupName -- name of the animation group the animation resides in
    animName -- name of the animation to select.

    """
    if not issueCommand('select -type "animgroup" -names "{0}"'.format(groupName)):
        raise FaceFXError('Could not select groupName "{0}"'.format(groupName))
    if not issueCommand('select -type "anim" -names "{0}"'.format(animName)):
        raise FaceFXError('Could not select animName "{0}"'.format(animName))


# Sets the current time in FaceFX Studio.
def setCurrentTime(time):
    """Sets the current time in FaceFX Studio."""
    if not issueCommand('currentTime -new {0}'.format(time)):
        raise FaceFXError('Setting current time failed.')


#-------------------------------------------------------------------------------
# These functions are helper functions that return additional data about the
# FaceFX Actor that is currently loaded in FaceFX Studio.
#-------------------------------------------------------------------------------

def getSelectedAnimGroupName():
    """Returns the name of the currently selected animation group in FaceFX
    Studio."""
    return getSelectedAnimation()[0]


def getSelectedAnimName():
    """Returns the name of the currently selected animation in FaceFX Studio."""
    return getSelectedAnimation()[1]


def getNumFaceGraphNodes():
    """Returns the number of Face Graph nodes contained in the actor loaded in
    FaceFX Studio."""
    return len(getFaceGraphNodeNames())


def getNumAnimationGroups():
    """Returns the number of animation groups contained in the actor loaded in
    FaceFX Studio."""
    return len(getAnimationNames())


def getNumAnimationsInGroup(groupName):
    """Returns the number of animations in the specified group contained in the
    actor loaded in FaceFX Studio."""
    numAnimations = 0
    animations = getAnimationNames()
    for animationGroup in animations:
        if animationGroup[0] == groupName:
            numAnimations = len(animationGroup[1])
    return numAnimations


def getNumTotalAnimations():
    """Returns the total number of animations contained in the actor loaded in
    FaceFX Studio."""
    numTotalAnimations = 0
    animations = getAnimationNames()
    for animationGroup in animations:
        numTotalAnimations += len(animationGroup[1])
    return numTotalAnimations

#-------------------------------------------------------------------------------
# These functions are called internally by FaceFX Studio. Do not remove them
# but feel free to modify them if you'd like to alter their behaviour; just
# make sure to adhere to the specifications for each one.
#-------------------------------------------------------------------------------


def shouldCompressAnimation(groupName, animName):
    """This is called internally by FaceFX Studio to determine if the animation
    should be compressed or not. Feel free to alter this check to do whatever
    you want, just make sure that you set the po_should_compress_animation
    hidden console variable to either yes or no.

    keyword arguments:

    groupName -- name of the animation group the animation resides in
    animName -- name of the animation to compress.

    """
    # By default all animations should be compressed.
    setConsoleVariableFast('po_should_compress_animation', 'yes')

    try:
        animDict = getAnimPythonDictionary(groupName, animName)
    except Exception, e:
        raise FaceFXError('{0}'.format(e))

    if animDict is not None:
        # If the animation has a Python dictionary, check to see if there
        # is a settings/compress key.
        try:
            shouldCompress = animDict['settings/compress']
            if type(shouldCompress) is bool:
                # There was a settings/compress key and it had an object of type bool, so use it for the setting.
                # Note that since the default above is 'yes' the only state we care about here is False so if
                # the value is False set the console variable to 'no'.
                if shouldCompress is False:
                    setConsoleVariableFast('po_should_compress_animation', 'no')
            else:
                # There was a settings/compress key but it was not a bool type!
                raise FaceFXError('shouldCompressAnimation("{0}", "{1}"): the animation has a Python dictionary with a settings/compress key but the object type is not bool!'.format(groupName, animName))
        except KeyError:
            # If the dictionary does not contain a settings/compress key
            # simply ignore the error telling us that the key does not
            # exist.
            pass
        except Exception, e:
            # Any other error is pretty serious.
            raise FaceFXError('{0}'.format(e))


#-------------------------------------------------------------------------------
# These functions are deprecated completely and throw when called.
#-------------------------------------------------------------------------------

def registerCallback(callback_name, callable_obj):
    raise FaceFXError('registerCallback() has been deprecated. Please update your code to use connectSignal().')


def unregisterCallback(callback_name):
    raise FaceFXError('unregisterCallback() has been deprecated. Please update your code to use disconnectSignal().')


def getCallback(callback_name):
    raise FaceFXError('getCallback() has been deprecated.')
