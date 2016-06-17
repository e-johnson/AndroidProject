# This script will create an analysis actor that outputs curves
# for speech targets with a "Cartoon Coarticulation" model.
# There is no blending between targets, just an immediate ramp
# to the phoneme's mapped value.  To use the script, set up your
# mapping from the Mapping tab how you want it, then run this
# script.  Save the resulting actor in the "Analysis Actors"
# folder so you can use it as an analysis actor.  If you do use
# the resulting analysis actor, make sure the actor you are using
# it on has a blank mapping, otherwise curves will be overdriven
# or overwritten with the default coarticulation results.

from FxStudio import *
import copy

phonemeMap = FxPhonemes.PhonemeMap()


class MappingPhoneme:
    def __init__(self, name, visemeTable):
        self.visemeTable = copy.deepcopy(visemeTable)
        self.name = name


class MappingTable:
    def __init__(self):
        self.phonemes = []
        phonemeMap = FxPhonemes.PhonemeMap()
        visemeTable = {}
        for entry in phonemeMap.entries:
            visemeTable[entry.targetName] = 0
        for entry in FxPhonemes.PHONEME_REGISTRY.entries:
            self.phonemes.append(MappingPhoneme(entry.facefxCoding, visemeTable))

    def addEntry(self, phonemeId, weight, target):
        self.phonemes[phonemeId].visemeTable[target] = weight


# Create combiner nodes for all targets in mapping
visemeTable = {}
for entry in phonemeMap.entries:
    visemeTable[entry.targetName] = 0
for key in visemeTable.keys():
    # Below we assume that no targets are driven below -1000 or above 1000
    FxStudio.issueCommand('graph -addnode -nodetype "FxCombinerNode" -name "%s" -max "1000" -min "-1000";' % (key))

# The amount to shoft phonemes by.
timeshift = -.05

issueCommand('animGroup -create -group "_PhonemeEventGroup";')
issueCommand('animGroup -create -group "_NoScalePhonemeEventGroup";')
issueCommand('animGroup -create -group "_ShiftedPhonemeEventGroup";')
for entry in FxPhonemes.PHONEME_REGISTRY.entries:
    issueCommand('anim -add -group "_PhonemeEventGroup" -name "%s";' % (entry.facefxCoding))
    issueCommand('anim -add -group "_NoScalePhonemeEventGroup" -name "%s";' % (entry.facefxCoding))
    issueCommand('anim -add -group "_ShiftedPhonemeEventGroup" -name "%s";' % (entry.facefxCoding))
    # Remove Duration Scale
    issueCommand('event -group "_PhonemeEventGroup" -anim "%s" -add -eventgroup "_NoScalePhonemeEventGroup" -eventanim "%s" -inheritdur "false";' % (entry.facefxCoding, entry.facefxCoding))
    # Shift by timeshift.  Use a very small duration so the phoneme transitions are instantaneous.
    issueCommand('event -group "_NoScalePhonemeEventGroup" -anim "%s" -add -eventgroup "_ShiftedPhonemeEventGroup" -persist "true" -eventanim "%s" -duration ".001" -start %f' % (entry.facefxCoding, entry.facefxCoding, timeshift))


mapping = MappingTable()
for entry in phonemeMap.entries:
    mapping.addEntry(entry.phonemeId, entry.mappingAmount, entry.targetName)

for phoneme in mapping.phonemes:
    for key in phoneme.visemeTable.keys():
        selectAnimation("_ShiftedPhonemeEventGroup", phoneme.name)
        issueCommand('curve -group "_ShiftedPhonemeEventGroup" -anim "%s" -add -name "%s" -owner "user";' % (phoneme.name, key))
        issueCommand('select -type "curve" -names "%s";' % (key))
        issueCommand('key -insert -default -time "0" -value "%f";' % (phoneme.visemeTable[key]))
        issueCommand('key -insert -default -time "1" -value "%f";' % (phoneme.visemeTable[key]))
