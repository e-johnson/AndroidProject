# The below python script is an example of how to automatically modify the
# analysis text before sending it into FaceFX Studio.  You can insert text tags,
# transliterate proper nouns, or search for phrases to key gestures.
import re
from FxStudio import *

negativeContractions = "aren't|can't|couldn't|didn't|doesn't|don't|hadn't|hasn't|haven't|isn't|mightn't|mustn't|shouldn't|wasn't|weren't|won't|wouldn't"
negativeWords = "no|not|none|neither|nor|never|nothing|nobody" + "|" + negativeContractions

# These are the emoticon and puncutation characters FaceFX recognizes.  Technically these are distinct lists, but combining
# them here for the purpose of finding emoticons and phrase punctuation to reinsert into the modified text will work.
# False matches will simply get placed back into the text stream unmolested like normal emoticons.
EMOTICON_CHARACTERS = ".!?,~`@#$%^&*()-_=+;:'\\"

'''
youWords = "you|your|you're|you've|you'd|thee"
meWords = "i|me|my|mine|we|our|us|i've|we've|we'd|i'd"
highWords = "peak|pinnacle|above|climax|highest|high|max|maximum|zenith|crest|mountain|hill|more|greater|exceeding|exceeded|increase|increasing|increased|maximize|boost|boosted|boosting|amplify|amplifying|amplified|enlarge|enlarging|enlarged"
lowWords = "low|down|under|below|short|small|little|squat|stumpy|beneath|underneath|reduce|reducing|reduced|cut|diminish|diminishing|diminished|less|lessen|lessened|lessening|decrease|decreasing|decreased|shrink|shrinking|shrunk|dwindle|dwindling|dwindled"
coordinating_conjunctions = " and | but | for | nor | or | so | yet "
correlative_conjunctions = " both | not only | either | neither | nor | whether | or "
subordinating_conjunctions_cause = " because | since | now that | as | in order that | so "
subordinating_conjunctions_opposition = " although | though | even though | whereas | while "
subordinating_conjunctions_condition = " if | unless | only if | whether or not | even if | in case "
phrase_delininators = coordinating_conjunctions + "|" + correlative_conjunctions + "|" + subordinating_conjunctions_cause + "|" + subordinating_conjunctions_opposition + "|" + subordinating_conjunctions_condition
relative_pronouns = " that | which | who | whom | whose | when | where | why "
prepositions = " aboard | about | above | across | after | against | along | amid | among | anti | around | as | at | before | behind | below | beneath | beside | besides | between | beyond | but | by | concerning | considering | despite | down | during | except | excepting | excluding | following | for | from | in | inside | into | like | minus | near | of | off | on | onto | opposite | outside | over | past | per | plus | regarding | round | save | since | than | through | to | toward | towards | under | underneath | unlike | until | up | upon | versus | via | with | within | without "
subphrase_delininators = relative_pronouns + "|" + prepositions
'''


class textTag():
    def __init__(self, tag):
        self.tag = tag
        self.wordindex = 0


def GetWordMeaningTags(analysisText):
    textTags = []
    tempAnalysisText = analysisText.lower()
    words = tempAnalysisText.split()

    flags = " blendin=.5 blendout=.5 duration=1.5 probability=.5 minstart=-.4 maxstart=-.1"
    wordindex = 0
    for word in words:
        match = re.search("\A(?:" + negativeWords + ")$", word)
        if match != None:
            tag = textTag("{\"_TextEvents|Negative\"" + flags + "}")
            tag.wordindex = wordindex
            textTags.append(tag)
        wordindex = wordindex + 1
    return textTags


def GetPreExistingTextTagsAndEmoticons(analysisText):

    textTags = []
    tagindex = 0

    tempAnalysisText = analysisText

    # find normal tags.
    textTagStrings = re.findall("{.+?}|\[.+?\]|<.+?>", tempAnalysisText)

    for textTagString in textTagStrings:
        pos = tempAnalysisText.find(textTagString)
        assert pos >= 0
        textTags.append(textTag(textTagString))
        tempAnalysisText = tempAnalysisText.replace(textTagString, " __text_tag_marker__ ", 1)

    # remove phrase punctuation and emoticons from the text so they aren't counted as words.
    # We do this after replacing normal tags with markers.
    tempAnalysisText = re.sub('([{emote_chars}]{{2,}})(\d{{2}})?'.format(emote_chars=re.escape(EMOTICON_CHARACTERS)), '', analysisText)

    if len(textTagStrings) > 0:
        # Find the corresponding word index the tag is at
        words = tempAnalysisText.split()
        wordindex = 0
        for word in words:
            if word == "__text_tag_marker__":
                textTags[tagindex].wordindex = wordindex
                tagindex = tagindex + 1
            # Make sure this is a real word, not some stranded punctuation or something that will get removed
            elif re.search("[a-zA-Z0-9]", word) != None:
                wordindex = wordindex + 1

    # Now remove normal tags and find the emoticons.
    tempAnalysisText = re.sub("{.+?}|\[.+?\]|<.+?>", "", analysisText)
    textTagStrings = re.findall('([{emote_chars}]{{2,}})(\d{{2}})?'.format(emote_chars=re.escape(EMOTICON_CHARACTERS)), tempAnalysisText)

    for textTagString in textTagStrings:
        fullString = textTagString[0] + textTagString[1]
        pos = tempAnalysisText.find(fullString)
        assert pos >= 0
        textTags.append(textTag(fullString))
        tempAnalysisText = tempAnalysisText.replace(fullString, " __text_tag_marker__ ", 1)

    # Find the corresponding word index the tag is at
    words = tempAnalysisText.split()
    wordindex = 0
    for word in words:
        if word == "__text_tag_marker__":
            textTags[tagindex].wordindex = wordindex
            tagindex = tagindex + 1
        # Make sure this is a real word, not some stranded punctuation or something that will get removed
        elif re.search("[a-zA-Z0-9]", word) != None:
            wordindex = wordindex + 1

    return textTags


def ReInsertTextTags(analysisText, textTags):
    # reinsert pre-existing text tags
    words = analysisText.split()
    analysisText = ""
    wordindex = 0
    for word in words:
        tagText = ""
        for tag in textTags:
            if wordindex == tag.wordindex:
                tagText = tagText + " " + tag.tag
        wordindex = wordindex + 1
        analysisText = analysisText + " " + tagText + " " + word + " "
    return analysisText


#-----------------------------------------------
# replace some common abbreviations with the full text.  Abbreviations should not be used in the text
# anyway and they will get in the way of figuring out when sentences begin and end.
#-----------------------------------------------
def ReplaceAbbreviations(analysisText):
    analysisText = re.sub("\sdr.\W", " doctor ", analysisText)
    analysisText = re.sub("\smr.\W", " mister ", analysisText)
    analysisText = re.sub("\smrs.\W", " misses ", analysisText)
    analysisText = re.sub("\sms.\W", " miss ", analysisText)
    analysisText = re.sub("\sjr.\W", " junior ", analysisText)
    analysisText = re.sub("\ssgt.\W", " sergeant ", analysisText)
    analysisText = re.sub("\ssr.\W", " senior ", analysisText)
    analysisText = re.sub("\svs.\W", " versus ", analysisText)
    return analysisText


def myAnalysisTextPreProcessor(analysisText, language):

    combinedTextTags = []

    # replace full stop unicode character with a period.
    analysisText = re.sub(u'\u3002', '.', analysisText)

    # cache the text tags before we convert to lower case.
    combinedTextTags = GetPreExistingTextTagsAndEmoticons(analysisText)
    # remove the tags.
    analysisText = re.sub("{.+?}|\[.+?\]|<.+?>", "", analysisText)
    analysisText = re.sub('([{emote_chars}]{{2,}})(\d{{2}})?'.format(emote_chars=re.escape(EMOTICON_CHARACTERS)), '', analysisText)

    # Convert any remainging quotes in the string to a double-single-quote emoticon.  Quotes aren't in our standard emoticon set
    # due to conflicts, but this will let us use the valuable information they contain.
    analysisText = re.sub('\"', ' \'\' ', analysisText)

    if language == "USEnglish" or languge == "UKEnglish":
        # Get rid of abbreviations.
        analysisText = ReplaceAbbreviations(analysisText)

    # replace pause punctuation with commas so the FaceFX-generated
    # phrase events take them into account.
    analysisText = re.sub('[;\:]|\s+-\s+', " , ", analysisText)

    # put extra spaces around punctuation (but not ' or - because these can be inside a word.)
    # also be careful not to put spaces around consecutive puncutation that will be an emoticon.
    analysisText = re.sub('([{0}][{1}][{0}])'.format(re.escape("^" + EMOTICON_CHARACTERS), re.escape(EMOTICON_CHARACTERS)),  ' \\1 ', analysisText)

    if language == "USEnglish" or languge == "UKEnglish":
        combinedTextTags.extend(GetWordMeaningTags(analysisText))

    analysisText = ReInsertTextTags(analysisText, combinedTextTags)

    return analysisText


def connectSignals():
    # Connect to the analysistextpreprocessor signal so that this function gets called before every analysis.
    connectSignal('analysistextpreprocessor', myAnalysisTextPreProcessor)


def disconnectSignals():
    # If we never connected, attempting to disconnect with raise an exception so catch it
    # and do nothing. This function is called from OnPostLoadActor.py to disconnect when
    # loading a new actor, so this prevents the output window from popping up and displaying
    # the exception.
    try:
        disconnectSignal('analysistextpreprocessor', myAnalysisTextPreProcessor)
    except RuntimeError:
        pass


connectSignals()
