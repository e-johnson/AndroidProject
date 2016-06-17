"""
Compiles per-phoneme confidence scores into a format useful for catching errors.

Returns an array of "error areas" where potential problem areas might be
Format: {  "startword",
           "endword",
           "starttime",
           "endtime",
           "maxerror",
           "anim",
           "group }

The array is sorted by maxerror, such that the most negative (worst) error is
first.

Owner: Doug Perkowski

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

from FxHelperLibrary import *
from FxAnimation import *
import FxPhonemes
from FxPhonemes import *

# This is the only threshold to tweak.  Increase it too much, and everything
# will be considered an error or error areas will include good results.  Decrease
# it too much and nothing will be considered an error or a single error will
# be broken up into smaller combinations of error and non-error sections.
CONFIDENCE_THRESHOLD = 40


def calculateAnimationErrorAreas(group, anim):
    animpath = '{0}/{1}'.format(group, anim)
    if not anim_exists(animpath):
        print "Animation does not exist!"
        return []

    errorAreas = []
    phoneme_word_list = FxPhonemes.PhonemeWordList(group, anim)

    wordindex = 0
    phonemeConfidences = []

    # smooth the confidence results by adding previous scores to current ones
    previous_confidence = []
    numPreviousConfidence = 6
    for i in xrange(1, numPreviousConfidence):
        previous_confidence.append(0)
    for word in phoneme_word_list.words:
        for phone in word.phonemes:
            if not hasattr(phone, 'confidence'):
                print 'Warning: no confidence scores available for anim {0} in group {1}.  Please reanalyze with latest version.'.format(anim, group)
                return []
            conf = phone.confidence

            if conf < 0:
                conf = CONFIDENCE_THRESHOLD

            # short phonemes aren't as important as long ones, but they
            # do indicate something is wrong in some cases.  Make sure all
            # phonemes even with very small duration have some impact.
            shortPhonemeWeight = .2
            dur = shortPhonemeWeight + phone.endTime - phone.startTime
            weightedConfidence = (conf - CONFIDENCE_THRESHOLD) * dur

            previous_confidence.pop(0)
            previous_confidence.append(weightedConfidence)
            summedConfidences = sum(previous_confidence)
            phonemeConfidences.append(summedConfidences)

    confidenceIndex = 0
    bIsError = False
    maxerror = 0
    wordindex = 0
    for word in phoneme_word_list.words:
        for phone in word.phonemes:
            if bIsError:
                if phonemeConfidences[confidenceIndex] > 0:
                    bIsError = False
                    maxerror = 0
                else:
                    maxerror += phonemeConfidences[confidenceIndex]
                    errorAreas[len(errorAreas) - 1]["maxerror"] = maxerror
                    errorAreas[len(errorAreas) - 1]["endword"] = wordindex
                    errorAreas[len(errorAreas) - 1]["endtime"] = word.endTime
            elif phonemeConfidences[confidenceIndex] < 0:
                    bIsError = True
                    errorAreas.append({"startword": wordindex,
                        "endword": wordindex,
                        "starttime": word.startTime,
                        "endtime": word.endTime,
                        "maxerror": phonemeConfidences[confidenceIndex],
                        "anim": anim,
                        "group": group})
            confidenceIndex += 1
        wordindex += 1
    return errorAreas


def sortErrors(errorAreas):
    def compareErrors(a, b):
        return cmp(a["maxerror"], b["maxerror"])
    errorAreas.sort(compareErrors)


def calculateConfidenceScores(animList):
    errorAreas = []
    for anim in animList:
        ga = FxHelperLibrary.split_animpath(anim)
        errorAreas += calculateAnimationErrorAreas(ga[0], ga[1])
        sortErrors(errorAreas)
    return errorAreas
