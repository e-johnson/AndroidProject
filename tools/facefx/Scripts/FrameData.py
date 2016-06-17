""" This module provides access to per-frame animation data from FaceFX Studio.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import getBoneFrame, getFaceGraphFrame, getSkeletonFrame, getBindPose
from FxMath import Vector, Quaternion


class NodeFrameData(object):
    """ Holds information about the state of a face graph node for the current animation frame in FaceFX Studio. """

    def __init__(self, nodeFrameDataTupleFromStudio):
        """ Initializes the node frame data from a tuple sent back from FaceFX Studio. """
        self.name = nodeFrameDataTupleFromStudio[0]
        self.value = nodeFrameDataTupleFromStudio[1]

    def __str__(self):
        """ Returns the string repsentation of the node frame data. """
        return '{0}: {1}'.format(self.name, self.value)


class FaceGraphFrame(object):
    """ Holds information about the state of all face graph nodes for the current animation frame in FaceFX Studio. """

    def __init__(self):
        """ Initializes the face graph frame from a tuple sent back from FaceFX Studio. """
        self.nodes = [NodeFrameData(n) for n in getFaceGraphFrame()]

    def __str__(self):
        """ Returns the string representation of the face graph frame. """
        r = ""
        nodeIndex = 0
        for node in self.nodes:
            r += "[" + str(nodeIndex) + "]: " + str(node) + "\n"
            nodeIndex += 1
        return r


class BoneFrameData(object):
    """ Holds information about the state of a FaceFX-controlled bone for the current animation frame in FaceFX Studio.

    The bone is given in local (parent) space.
    weight is the currently calculated weight that FaceFX is using for the bone.

    """

    def __init__(self, boneFrameDataTupleFromStudio):
        """ Initializes the bone frame data from a tuple sent back from FaceFX Studio. """
        self.name = boneFrameDataTupleFromStudio[0]
        self.position = Vector(boneFrameDataTupleFromStudio[1])
        self.rotation = Quaternion(boneFrameDataTupleFromStudio[2])
        self.scale = Vector(boneFrameDataTupleFromStudio[3])
        self.weight = boneFrameDataTupleFromStudio[4]

    def __str__(self):
        """ Returns the string repsentation of the bone frame data. """
        return '{0}:\n        position: {1}\n        rotation: {2}\n        scale: {3}\n        weight: {4}'.format(self.name, self.position, self.rotation, self.scale, self.weight)


class BoneFrame(object):
    """ Holds information about the state of all FaceFX-controlled bones for the current animation frame in FaceFX Studio. """

    def __init__(self):
        """ Initializes the bone frame from a tuple sent back from FaceFX Studio. """
        self.bones = [BoneFrameData(b) for b in getBoneFrame()]

    def __str__(self):
        """ Returns the string representation of the bone frame. """
        r = ""
        boneIndex = 0
        for bone in self.bones:
            r += "[" + str(boneIndex) + "]: " + str(bone) + "\n"
            boneIndex += 1
        return r


class AnimationFrame(object):
    """ Holds information about the state of all face graph nodes and all FaceFX-controlled bones for the current animation frame in FaceFX Studio. """

    def __init__(self):
        """ Initializes the animation frame with a face graph frame and a bone frame sent back from FaceFX Studio. """
        self.faceGraphFrame = FaceGraphFrame()
        self.boneFrame = BoneFrame()

    def __str__(self):
        """ Returns the string representation of the animation frame. """
        return "==============[ Face Graph Frame ]==============\n" + str(self.faceGraphFrame) + "==============[ Bone Frame ]==============\n" + str(self.boneFrame)


class SkeletonFrameData(object):
    """ Holds information about the state of the entire skeleton for the current animation frame in FaceFX Studio.

    The bone is given in local (parent) space.

    """

    def __init__(self, skeletonFrameDataTupleFromStudio):
        """ Initializes the skeleton frame data from a tuple sent back from FaceFX Studio. """
        self.name = skeletonFrameDataTupleFromStudio[0]
        self.position = Vector(skeletonFrameDataTupleFromStudio[1])
        self.rotation = Quaternion(skeletonFrameDataTupleFromStudio[2])
        self.scale = Vector(skeletonFrameDataTupleFromStudio[3])
        self.parentName = str(skeletonFrameDataTupleFromStudio[4])
        self.parent = None

    def __str__(self):
        """ Returns the string representation of the skeleton frame data. """
        return '{0}:\n        position: {1}\n        rotation: {2}\n        scale: {3}\n        parent: {4}'.format(self.name, self.position, self.rotation, self.scale, self.parentName)


class SkeletonFrame(object):
    """ Holds information about the state of the entire skeleton for the current animation frame in FaceFX Studio. """

    def __init__(self, forceBindPose=False):
        """ Initializes the skeleton frame from a tuple sent back from FaceFX Studio. """
        if forceBindPose == True:
            self.bones = [SkeletonFrameData(b) for b in getBindPose()]
        else:
            self.bones = [SkeletonFrameData(b) for b in getSkeletonFrame()]
        # Link up all of the bones in the skeleton.
        for bone in self.bones:
            if bone.parentName != "None":
                parent = [p for p in self.bones if p.name == bone.parentName]
                if len(parent) == 1:
                    bone.parent = parent[0]
                else:
                    raise RuntimeError("Skeleton hierarchy error in FrameData.SkeletonFrame!")

    def __str__(self):
        """ Returns the string representation of the skeleton frame. """
        r = ""
        boneIndex = 0
        for bone in self.bones:
            r += "[" + str(boneIndex) + "]: " + str(bone) + "\n"
            boneIndex += 1
        return r


class SkeletonBindPose(SkeletonFrame):
    """ Holds information about the state of the entire skeleton in its bind pose in FaceFX Studio. """

    def __init__(self):
        """ Initializes the skeleton reference frame from a tuple sent back from FaceFX Studio. """
        SkeletonFrame.__init__(self, True)
