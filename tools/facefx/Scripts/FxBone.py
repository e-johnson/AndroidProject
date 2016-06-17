""" This module provides access to the rest pose and individual bone poses from FaceFX Studio.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import getRestPose, getBonePoseFrame
from FxMath import Vector, Quaternion


class Bone(object):
    """ A bone.

    The bone is given in local (parent) space.

    instance variables:

    name - the name of the bone
    position - the vector position of the bone
    rotation - the quaternion rotation of the bone
    scale - the vector scale of the bone

    """

    def __init__(self, boneTupleFromStudio):
        """ Initializes the bone from a tuple sent back from FaceFX Studio. """
        self.name = boneTupleFromStudio[0]
        self.position = Vector(boneTupleFromStudio[1])
        self.rotation = Quaternion(boneTupleFromStudio[2])
        self.scale = Vector(boneTupleFromStudio[3])

    def __str__(self):
        """ Returns the string repsentation of the bone. """
        return '{0}:\n        position: {1}\n        rotation: {2}\n        scale: {3}'.format(self.name, self.position, self.rotation, self.scale)


class RestPose(object):
    """ Holds information about the rest pose from FaceFX Studio.

    instance variables:

    bones - a list of the bones in the rest pose

    """

    def __init__(self):
        """ Initializes the rest pose from a tuple sent back from FaceFX Studio. """
        self.bones = [Bone(b) for b in getRestPose()]

    def __str__(self):
        """ Returns the string representation of the rest pose. """
        return '\n'.join(['[{0}]: {1}'.format(index, bone) for index, bone in enumerate(self.bones)])


class BonePose(object):
    """ Holds information about a particular bone pose from FaceFX Studio.

    instance variables:

    bones - a list of the bones in the bone pose

    """

    def __init__(self, bonePoseName):
        """ Initializes the bone pose from a tuple sent back from FaceFX Studio. """
        self.name = bonePoseName
        self.bones = [Bone(b) for b in getBonePoseFrame(bonePoseName)]

    def __str__(self):
        """ Returns the string representation of the bone pose. """
        return '\n'.join(['[{0}]: {1}'.format(index, bone) for index, bone in enumerate(self.bones)])
