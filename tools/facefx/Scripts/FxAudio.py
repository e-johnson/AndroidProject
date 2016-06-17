""" This module provides access to the audio that is loaded in FaceFX Studio.

classes:

Audio -- A wrapper around the currently selected audio in FaceFX Studio.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import FaceFXError


class Audio(object):
    """ A wrapper around the currently selected audio in FaceFX Studio.

    instance variables:

    audioPath -- the path to the audio file
    numChannels -- the number of channels in the audio
    bitsPerSample -- the number of bits in each sample of the audio
    sampleRate -- the sample rate of the audio in Hz
    samples -- a tuple of the samples in the audio as floats

    """

    def __init__(self):
        """ Initialize the object by loading the currently selected audio.
        """
        from FxStudio import getAudio
        at = getAudio()
        try:
            self.audioPath = at[0]
            self.numChannels = at[1]
            self.bitsPerSample = at[2]
            self.sampleRate = at[3]
            self.samples = at[4]
        except IndexError:
            raise FaceFXError('No animation selected in FaceFX Studio.')

    def __str__(self):
        """ Return the string representation of the object.
        """
        return 'Audio: {0} ({1}kHz {2} bit {3} channel{4}, {5} seconds)'.format(
            self.audioPath, self.sampleRate / 1000, self.bitsPerSample,
            self.numChannels, 's' if self.numChannels > 1 else '',
            self.getDuration())

    def getNumSamples(self):
        """ Return the number of samples in the audio.
        """
        return len(self.samples)

    def getDuration(self):
        """ Return the duration of the audio clip in seconds.
        """
        return float(self.getNumSamples()) / self.sampleRate
