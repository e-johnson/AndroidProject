""" This module provides wrappers around various mathematical concepts used in FaceFX animation data.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""


class Vector(object):
    """ A wrapper around a 3-dimensional vector.

    instance variables:

    x - the x component of the vector
    y - the y component of the vector
    z - the z component of the vector

    """

    def __init__(self, vectorTupleFromStudio):
        """ Initializes the vector from a tuple sent back from FaceFX Studio.

        parameters:

        vectorTupleFromStudio -- A tuple (x, y, z)

        """
        self.x, self.y, self.z = vectorTupleFromStudio

    def __str__(self):
        """ Returns the string representation of the vector. """
        return '<x={0}, y={1}, z={2}>'.format(self.x, self.y, self.z)

    def __repr__(self):
        """ Returns the Python representation of the vector. """
        return 'Vector(({0}, {1}, {2}))'.format(self.x, self.y, self.z)


class Quaternion(object):
    """ A wrapper around a quaternion.

    instance variables:

    w - the w component of the quaternion
    x - the x component of the quaternion
    y - the y component of the quaternion
    z - the z component of the quaternion

    """

    def __init__(self, quaternionTupleFromStudio):
        """ Initializes the quaternion from a tuple sent back from FaceFX Studio.

        parameters:

        quaternionTupleFromStudio -- A tuple (w, x, y, z)

        """
        self.w, self.x, self.y, self.z = quaternionTupleFromStudio

    def __str__(self):
        """ Returns the string represenation of the quaternion. """
        return '<w={0}, x={1}, y={2}, z={3}>'.format(self.w, self.x, self.y, self.z)

    def __repr__(self):
        """ Returns the Python representation of the quaternion. """
        return 'Quaternion(({0}, {1}, {2}, {3}))'.format(self.w, self.x, self.y, self.z)
