""" This module provides definitions for phonemes, phoneme lists, and word lists

static variables:

PHONEME_REGISTRY -- A PhonemeRegistry object that has been initialized

classes:

PhonemeType -- Information about a specific type of phoneme
PhonemeRegistry -- Provides a mapping from phonemeID or facefxCoding to
    PhonemeType objects
PhonemeMapEntry -- A single entry in a PhonemeMap, maps a phoneme to a target by
    an amount
PhonemeMap -- The actor's mapping from phonemes to targets
Phoneme -- A single phoneme in the PhonemeList
PhonemeList -- A sorted list of the phonemes in an animation
Word -- A single word in the PhonemeWordList
PhonemeWordList -- A sorted list of the phonemes and words in an animation

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio
import FxHelperLibrary


class PhonemeType:
    """ Provides information about a specific type of phoneme.

    instance variables:

    phonemeId -- the int id assigned to the phoneme
    facefxCoding -- the FaceFX coding of the phoneme
    ipaCoding -- the IPA coding of the phoneme
    sampaCoding -- the X-SAMPA coding of the phoneme
    durationMean -- the mean duration of the phoneme
    durationStddev -- the standard devaition of the duration of the phoneme.

    """

    def __init__(self, phonemeTypeTupleFromStudio):
        """ Initializes the object with the tuple from Studio. """
        self.phonemeId = phonemeTypeTupleFromStudio[0]
        self.facefxCoding = phonemeTypeTupleFromStudio[1]
        self.ipaCoding = phonemeTypeTupleFromStudio[2]
        self.sampaCoding = phonemeTypeTupleFromStudio[3]
        self.durationMean = phonemeTypeTupleFromStudio[4]
        self.durationStddev = phonemeTypeTupleFromStudio[5]

    def __str__(self):
        """ Returns the string representation of the PhonemeType """
        return 'id={0}  facefxCoding={1}  ipaCoding={2}  sampaCoding={3}  durationMean={4}  durationStddev={5}'.\
            format(self.phonemeId, self.facefxCoding, self.ipaCoding,
                self.sampaCoding, self.durationMean, self.durationStddev)

    def __repr__(self):
        """ Hackish repr to make it look nice in the interpreter. """
        return '[{0} {1}]'.format(self.phonemeId, self.facefxCoding)

    def getPhonemeClass(self):
        """ Returns the class of the PhonemeType as a string.

        Valid returns are 'vowel', 'diphthong', 'fricative', 'nasal',
        'approximate', 'stop', 'trill', 'silence', and 'unknown'
        """
        return FxStudio.getPhonemeClass(self.phonemeId)

    def getSampleWords(self):
        """ Returns a string containing sample words that use the phoneme. """
        return FxStudio.getPhonemeSampleWords(self.phonemeId)

    def getClassification(self):
        """ Returns the classification string for the phoneme. """
        return FxStudio.getPhonemeClassification(self.phonemeId)

    def isVowel(self):
        """ Returns True if the class is a vowel or a diphthong. """
        return self.getPhonemeClass() == 'vowel' or\
            self.getPhonemeClass() == 'diphthong'

    def isDiphthong(self):
        """ Returns True if the class is a diphthong. """
        return self.getPhonemeClass() == 'diphthong'

    def isFricative(self):
        """ Returns True if the class is a fricative. """
        return self.getPhonemeClass() == 'fricative'

    def isNasal(self):
        """ Returns True if the class is a nasal. """
        return self.getPhonemeClass() == 'nasal'

    def isApproximate(self):
        """ Returns True if the class is an approximate. """
        return self.getPhonemeClass() == 'approximate'

    def isStop(self):
        """ Returns True if the class is a stop. """
        return self.getPhonemeClass() == 'stop'

    def isTrill(self):
        """ Returns True if the class is a trill. """
        return self.getPhonemeClass() == 'trill'

    def isSilence(self):
        """ Returns True if the class is silence. """
        return self.getPhonemeClass() == 'silence'


class PhonemeRegistry:
    """ Provides a mapping from phonemeID to PhonemeType.

    When FaceFX Studio starts up, a global phoneme registry is created as
    FxPhonemes.PHONEME_REGISTRY. The PHONEME_REGISTRY may be indexed by
    PhonemeType.phonemeId or PhonemeType.facefxCoding.

    instance variables:

    entries - a list of phoneme types sorted by id

    """

    def __init__(self):
        """ Initializes the object by pulling the data from FaceFX Studio """
        phonemeTypeTuplesFromStudio = FxStudio.getPhonemeRegistry()
        self.entries = [PhonemeType(entry)
            for entry in phonemeTypeTuplesFromStudio]
        # Use a dictionary to help map phonemeIDs and facefx codings to indices
        self._redirect = dict()
        for e in self.entries:
            self._redirect[e.phonemeId] = e.phonemeId
            self._redirect[e.facefxCoding] = e.phonemeId

    def __str__(self):
        """ Returns the string representation of the object. """
        return '\n'.join([str(x) for x in self.entries])

    def __getitem__(self, item):
        """ Returns the entry specified by item, either phonemeID or
        facefxCoding
        """
        return self.entries[self._redirect[item]]

    def getNumEntries(self):
        """ Returns the number of entries in the registry. """
        return len(self.entries)

    def findPhonemeTypeByFaceFXCoding(self, facefxCoding):
        """ Returns the PhonemeType with the specified facefxCoding, or None """
        for entry in self.entries:
            if entry.facefxCoding == facefxCoding:
                return entry
        print 'Error: Unregistered facefx phoneme coding detected [ ' + facefxCoding + ' ]!'
        return None

    def findPhonemeTypeByIPACoding(self, ipaCoding):
        """ Returns the PhonemeType with the specified ipaCoding, or None """
        for entry in self.entries:
            if entry.ipaCoding == ipaCoding:
                return entry
        print 'Error: Unregistered ipa phoneme coding detected [ ' + ipaCoding + ' ]!'
        return None

    def findPhonemeTypeBySampaCoding(self, sampaCoding):
        """ Returns the PhonemeType with the specified sampaCoding, or None """
        for entry in self.entries:
            if entry.sampaCoding == sampaCoding:
                return entry
        print 'Error: Unregistered sampa phoneme coding detected [ ' + sampaCoding + ' ]!'
        return None


class PhonemeMapEntry:
    """ Represents a single mapping entry.

    instance variables:

    phonemeId -- the integer ID of the phoneme
    targetName -- the name of the target to drive
    mappingAmount -- a float value indicated the value of the target

    """
    def __init__(self, phonemeMapTupleFromStudio):
        """ Initialize the PhonemeMapEntry with the tuple from Studio. """
        self.phonemeId = phonemeMapTupleFromStudio[0]
        self.targetName = phonemeMapTupleFromStudio[1]
        self.mappingAmount = phonemeMapTupleFromStudio[2]

    def __str__(self):
        """ Returns a string representation of the mapping entry. """
        return 'phoneme={0} => targetName={1}  mappingAmount={2}'.format(
            # PEP8 note: this is not an undefined name -- it is defined in
            # the C++ side of the FxPhoneme module.
            PHONEME_REGISTRY[self.phonemeId].facefxCoding, self.targetName,
            self.mappingAmount)

    def __repr__(self):
        """ Returns a hackish representation of the mapping entry """
        return 'PhonemeMapEntry(({0}, {1}, {2}))'.format(
            # PEP8 note: this is not an undefined name -- it is defined in
            # the C++ side of the FxPhoneme module.
            PHONEME_REGISTRY[self.phonemeId].facefxCoding, self.targetName,
            self.mappingAmount)


class PhonemeMap:
    """ Represents an actor's phoneme map.

    instance variables:
    entries -- a list of non-zero PhonemeMapEntry

    """

    def __init__(self):
        """ Initialize the phoneme map by pulling the data from Studio. """
        phonemeMapTuplesFromStudio = FxStudio.getPhonemeMap()
        self.entries = [PhonemeMapEntry(e) for e in phonemeMapTuplesFromStudio]
        # Sort the map entries in ascending order by phonemeId using a
        # simple lambda function passed to sort().
        self.entries.sort(lambda this, next: this.phonemeId - next.phonemeId)

    def __str__(self):
        """ Returns the string representation of the phoneme map. """
        return '\n'.join([str(entry) for entry in self.entries])

    def getNumEntries(self):
        """ Returns the number of entries in the phoneme map. """
        return len(self.entries)

    def getMappingAmount(self, phonemeId, targetName):
        """ Returns the amount that phonemeId is mapped to targetName.

        If there is no explicit entry between phonemeId and targetName, it is
        assumed that the mapping amount is 0.0.

        keyword arguments:

        phonemeId -- the integer identifier of the phoneme to search for
        targetName -- the name of the target to search for
        """
        for entry in self.entries:
            if entry.phonemeId == phonemeId and entry.targetName == targetName:
                return entry.mappingAmount
        return 0.0

    def getTargetNamesUsedInMapping(self):
        """ Returns a tuple of targetNames that are involved in the mapping.

        The tuple returned contains no duplicates. An empty tuple is returned
        if there is no mapping.
        """
        return tuple(set([entry.targetName for entry in self.entries]))

    def getTargetsMappedToPhonemeId(self, phonemeId):
        """ Returns a list of tuples that are mapped to the phonemeId.

        The list is in the format [(targetName, mappingAmount), *], or an empty
        list if no targets are explicitly mapped to the given phonemeId. In that
        case it should be assumed that the mapping value is 0.0 for each target.

        keyword arguments:

        phonemeId -- the integer identifier of the phoneme to search for
        """
        return [(e.targetName, e.mappingAmount) for e in self.entries if
            e.phonemeId == phonemeId]

    def getPhonemeIdsMappedToTarget(self, targetName):
        """ Returns a list of tuples that are mapped to the targetName.

        The list is in the format [(phonemeId, mappingAmount), *], or an empty
        list if no phonemeIds are explicitly mapped to the given targetName. In
        that case it should be assumed that the mapped value is 0.0 for each
        phonemeId.

        keyword arguments:

        targetName -- the name of the target to search for.
        """
        return [(e.phonemeId, e.mappingAmount) for e in self.entries if
            e.targetName == targetName]


class Phoneme:
    """ Rrepresents a single phoneme in a list.

    instance variables:
    phonemeId -- the integer identifier of the phoneme
    startTime -- the time the phoneme starts, in seconds
    endTime -- the time the phoneme ends, in seconds
    confidence -- the confidence score of the phoneme

    """

    def __init__(self, phonemeTupleFromStudio):
        """ Initialize the object with the tuple from Studio. """
        self.phonemeId = phonemeTupleFromStudio[0]
        self.startTime = phonemeTupleFromStudio[1]
        self.endTime = phonemeTupleFromStudio[2]
        self.confidence = phonemeTupleFromStudio[3]

    def __str__(self):
        """ Returns a string representation of the phoneme. """
        return 'phoneme={0}  startTime={1}  endTime={2}  confidence={3}'.format(
            # PEP8 note: this is not an undefined name -- it is defined in
            # the C++ side of the FxPhoneme module.
            PHONEME_REGISTRY[self.phonemeId].facefxCoding, self.startTime,
            self.endTime, self.confidence)

    def __repr__(self):
        """ Returns a hackish representation of the phoneme. """
        return '[{0} ({1}, {2}) {3}]'.format(
            # PEP8 note: this is not an undefined name -- it is defined in
            # the C++ side of the FxPhoneme module.
            PHONEME_REGISTRY[self.phonemeId].facefxCoding, self.startTime,
            self.endTime, self.confidence)

    def getDuration(self):
        """ Returns the duration of the phoneme in seconds. """
        return self.endTime - self.startTime

    def getFacefxCoding(self):
        """ Returns the FaceFX coding of the phoneme. """
        # PEP8 note: this is not an undefined name -- it is defined in
        # the C++ side of the FxPhoneme module.
        return PHONEME_REGISTRY[self.phonemeId].facefxCoding

    def estimatePercentile(self):
        """ Returns the estimated percentile of the phoneme's duration compared
        to others of the same type. """
        return FxHelperLibrary.estimate_percentile(
            # PEP8 note: this is not an undefined name -- it is defined in
            # the C++ side of the FxPhoneme module.
            self.getDuration(), PHONEME_REGISTRY[self.phonemeId].durationMean,
            PHONEME_REGISTRY[self.phonemeId].durationStddev)


class PhonemeList:
    """ Represents a chronologically sorted list of phonemes in an animation.

    instance variables:
    phonemes -- a list of Phoneme objects

    """

    def __init__(self, animGroupName, animName):
        """ Initializes the object by grabbing the data from Studio. """
        phonemeTuplesFromStudio = FxStudio.getPhonemeList(animGroupName,
            animName)
        self.phonemes = [Phoneme(p) for p in phonemeTuplesFromStudio]

    def __str__(self):
        """ Returns a string representation of the phoneme list. """
        return ' '.join([p.getFacefxCoding() for p in self.phonemes])

    def __len__(self):
        """ Returns the number of phonemes in the list. """
        return len(self.phonemes)

    def getNumPhonemes(self):
        """ Returns the number of phonemes in the list. """
        return len(self)


class Word:
    """ Represents a word in a list.

    instance variables:

    word -- a string containing the word's text
    startTime -- the time the word starts, in seconds
    endTime -- the time the word ends, in seconds
    phonemes -- a list of the Phoneme objects comprising the word

    """

    def __init__(self, wordTupleFromStudio, phonemes=[]):
        """ Initializes the word with a tuple from Studio and the list of the
        phonemes in the word.
        """
        self.word = wordTupleFromStudio[0]
        self.startTime = wordTupleFromStudio[1]
        self.endTime = wordTupleFromStudio[2]
        self.phonemes = [Phoneme(p) for p in phonemes]

    def __str__(self):
        """ Returns the string representation of the word. """
        return 'word={0}  startTime={1}  endTime={2}'.format(self.word,
            self.startTime, self.endTime)

    def getDuration(self):
        """ Returns the duration of the word, in seconds. """
        return self.endTime - self.startTime


# This class represents a list of phonemes and a list of words and
# is inherited from the PhonemeList class.
class PhonemeWordList(PhonemeList):
    """ Represents a chronologically sorted list of phonemes and words in the
    animation.

    instance variables:

    phonemes -- a list of Phoneme objects
    words -- a list of Word objects

    """

    def __init__(self, animGroupName, animName):
        """ Initialize the object by pulling the data from Studio. """
        PhonemeList.__init__(self, animGroupName, animName)
        wordTuplesFromStudio = FxStudio.getWordList(animGroupName, animName)
        self.words = [
            Word(w, FxStudio.getPhonemesInWord(animGroupName, animName, i))
            for i, w in enumerate(wordTuplesFromStudio)]

    def __str__(self):
        """ Returns a string representation of the PhonemeWordList. """
        r = ' '.join(word.word for word in self.words)
        r += '\n'
        r += PhonemeList.__str__(self)
        return r

    def getNumWords(self):
        """ Returns the number of words in the PhonemeWordList. """
        return len(self.words)
