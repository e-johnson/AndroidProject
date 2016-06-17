"""
A substitute phoneme list with more pythonic functionality.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import FxStudio
import FxHelperLibrary

from FxPhonemes import PHONEME_REGISTRY


# Phoneme structures
class PhonemeInList(object):

    """ A single phoneme in a phoneme list.
    """

    def __init__(self, phonemeTuple):
        self.id = phonemeTuple[0]
        self.start_time = phonemeTuple[1]
        self.weight = 1.0
        self.archetype = 'NONE'

    def __repr__(self):
        """ Abuse __repr__ to get a nice look printed python list. """
        #return 'PhonemeInList((%d, %0.3f))' % \
        #    (self.id, self.start_time)
        return self.__str__()

    def __str__(self):
        return '[%s (%s) %0.3f %0.2f]' % \
            (self.facefx_coding(), self.archetype, self.start_time, self.weight)

    def facefx_coding(self):
        return PHONEME_REGISTRY[self.id].facefxCoding

    def set_id(self, new_id, archetypes):
        self.id = new_id
        facefx_coding = self.facefx_coding()
        for k, v, in archetypes.iteritems():
            if facefx_coding in v:
                self.archetype = k


class StandalonePhoneme(object):

    """ A phoneme in its full representation outside of the phoneme list.
    """

    def __init__(self, phoneme_in_list, end_time):
        self.id = phoneme_in_list.id
        self.start_time = phoneme_in_list.start_time
        self.end_time = end_time
        self.weight = phoneme_in_list.weight
        self.archetype = phoneme_in_list.archetype

    def __str__(self):
        return '%s [%s] [%f, %f] (w=%f)' % \
            (self.facefx_coding(), self.archetype, self.start_time, self.end_time, self.weight)

    def facefx_coding(self):
        return PHONEME_REGISTRY[self.id].facefxCoding

    def duration(self):
        return self.end_time - self.start_time


class PhonemeList(object):

    """ A list of phonemes.

    The class is designed to store both the list of phonemes and the total
    boundaries of the phoneme list. The start time of a phoneme list is always
    zero seconds.
    """

    def __init__(self, phoneme_list=None, list_end_time=None):
        """ Initializes the phoneme list.
        """
        self.end_time = 0 if list_end_time is None else list_end_time
        self.phonemes = list() if phoneme_list is None else phoneme_list

    @classmethod
    def load_from_anim(cls, anim_path):
        """ Creates a phoneme list from a given animation.

        anim_path is formatted [animGroup]/[animation].
        """
        animGroupName, animName = FxHelperLibrary.split_animpath(anim_path)
        phoneme_tuples = FxStudio.getPhonemeList(animGroupName, animName)
        if len(phoneme_tuples) == 0:
            return PhonemeList()
        phoneme_list = [PhonemeInList(p) for p in phoneme_tuples]
        return PhonemeList(phoneme_list, phoneme_tuples[-1][2])

    def __str__(self):
        """ String representation of the phoneme list.
        """
        return ' '.join(['%s(%s)' % (p.facefx_coding(), p.archetype)
            for p in self.phonemes])

    def __len__(self):
        """ Returns the number of phonemes in the phoneme list.
        """
        return len(self.phonemes)

    def __getitem__(self, item):
        """ Returns a single item from a phoneme list.
        """
        if isinstance(item, slice):
            indices = item.indices(len(self))
            phonemes = [self.phonemes[i] for i in range(*indices)]
            return PhonemeList(phonemes, self.end_time)
        else:
            end_time = self.phonemes[item + 1].start_time if item < len(self.phonemes) - 1 else self.end_time
            return StandalonePhoneme(self.phonemes[item], end_time)

    def duration(self):
        """ Returns the total duration of the phoneme list in seconds.
        """
        return self.end_time

    def assign_archetypes(self, archetypes):
        """ Assigns the archetype of the phone based on the dictionary. """
        for p in self.phonemes:
            for k, v, in archetypes.iteritems():
                if p.facefx_coding() in v:
                    p.archetype = k

    def filter(self, test):
        """ Filters the list to include only the phonemes that pass the test.
        """
        phonemes = [p for p in self.phonemes if test(p)]
        return PhonemeList(phonemes, self.end_time)

    def score(self):
        """ Assigns the weight of each phoneme to the percentile in which its
        duration falls.
        """
        count = 0
        for p in self.phonemes:
            duration = self[count].duration()
            mu = PHONEME_REGISTRY[p.id].durationMean
            sigma = PHONEME_REGISTRY[p.id].durationStddev
            p.weight = FxHelperLibrary.estimate_percentile(duration, mu, sigma)
            count += 1


class Word(object):

    """ A single word in a list. """

    def __init__(self, text, start, end):
        """ Initializes the word with the text and start and end times. """
        self.text = text
        self.start_time = start
        self.end_time = end

    def __repr__(self):
        return '{0} [{1}, {2}]'.format(self.text, self.start_time, self.end_time)

    def __str__(self):
        return self.__repr__()


class WordList(object):

    """ A list of words. A simple wrapper around the tuple provided from FaceFX
    Studio. """

    def __init__(self, word_list=None):
        self.words = list() if word_list is None else word_list

    @classmethod
    def load_from_anim(cls, anim_path):
        """ Creates a word list from a given animation.

        anim_path is formatted [anim_group]/[animation]
        """
        animGroupName, animName = FxHelperLibrary.split_animpath(anim_path)
        word_tuples = FxStudio.getWordList(animGroupName, animName)
        if len(word_tuples) == 0:
            return WordList()
        word_list = [Word(x[0], x[1], x[2]) for x in word_tuples]
        return WordList(word_list)

    def __str__(self):
        return ' '.join(str(x) for x in self.words)

    def __len__(self):
        """ Returns the number of words in the list. """
        return len(self.words)

    def __getitem__(self, item):
        """ Returns a single word from the list. """
        if isinstance(item, slice):
            indices = item.indices(len(self))
            return WordList([self.words[i] for i in range(*indices)])
        else:
            return self.words[item]
