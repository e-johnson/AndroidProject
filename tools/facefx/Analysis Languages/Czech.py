# -*- coding: utf-8 -*-
#
# A Czech language pronouncer.
#
# Jamie Redmond
# Copyright (c) 2002-2012 OC3 Entertainment, Inc.
# -----------------------------------------------

from FxStudio import *
from FxAnalysis import *
import re

czech_ipa_map = { u'a'  : u'a',
                  u'á'  : u'a',
                  u'b'  : u'b',
                  u'c'  : u'ʦ',
                  u'č'  : u'ʧ',
                  u'd'  : u'd',
                  u'ď'  : u'ɟ',
                  u'd\'': u'ɟ', # d' is here for completeness but it is replaced with ď during processing.
                  u'e'  : u'ɛ',
                  u'é'  : u'ɛ',
                  u'ě'  : [u'j', u'ɛ'],
                  u'f'  : u'f',
                  u'g'  : u'ɡ',
                  u'h'  : u'ɦ',
                  u'H'  : u'x', # ch is replaced by H during processing.
                  u'i'  : u'ɪ',
                  u'í'  : u'ɪ',
                  u'j'  : u'j',
                  u'k'  : u'k',
                  u'l'  : u'l',
                  u'm'  : u'm',
                  u'n'  : u'n',
                  u'ň'  : u'ɲ',
                  u'N'  : u'ŋ', # n is replaced with N when it precedes k or g during processing.
                  u'o'  : u'o',
                  u'ó'  : u'o',
                  u'p'  : u'p',
                  u'q'  : [u'k', u'v'], # q is here for completeness but this expansion is made explicitly during processing.
                  u'r'  : u'r',
                  u'ř'  : u'r', # we may want to change this...
                  u's'  : u's',
                  u'š'  : u'ʃ',
                  u't'  : u't',
                  u'ť'  : u'c',
                  u't\'': u'c', # t' is here for completeness but it is replaced with ť during processing.
                  u'u'  : u'u',
                  u'ú'  : u'u',
                  u'ů'  : u'u',
                  u'v'  : u'v',
                  u'w'  : u'v',
                  u'x'  : [u'k', u's'], # x is here for completeness but this expansion is made explicitly during processing.
                  u'y'  : u'ɪ',
                  u'ý'  : u'ɪ',
                  u'z'  : u'z',
                  u'ž'  : u'ʒ',
                  u'Z'  : u'ʣ', # dz is replace by Z during processing.
                  u'Ž'  : u'ʤ', # dž is replaced by Ž during processing.
                  u'A'  : [u'ɪ', u'j', u'a'], # ia is replaced by A during processing.
                  u'E'  : [u'ɪ', u'j', u'ɛ'], # ie is replaced by E during processing.
                  u'I'  : [u'ɪ', u'j', u'ɪ'], # ii is replaced by I during processing.
                  u'O'  : [u'ɪ', u'j', u'o'], # io is replaced by O during processing.
                  u'U'  : [u'ɪ', u'j', u'u'], # iu is replaced by U during processing.
                  u'Y'  : [u'ɔ', u'ɪ'], # oj is replaced by Y during processing.
                  u'#'  : [u'e', u'ɪ'], # ej is replaced by # during processing.
                  u'$'  : [u'j', u'e', u'ɪ'], # ěj is replaced by $ during processing.
                  u'%'  : [u'u', u'ɪ'], # uj, új, and ůj are replaced by % during processing.
                  u'&'  : [u'o', u'ʊ'] } # ou is replaced by & during processing.


# Note the fact that ř does not appear in the following string and maps is intentional.

# The following string contains both voiced and unvoiced consonants that are relevant to morphing rules.
# The characters that are true Unicode need to be escaped in this string because it is used as the basis
# of a regular expression and Python does not allow non-escaped Unicode characters in regular expression
# patterns.

#                           ur'bpdtgkzsZcvfďťhHžšŽč'
morphing_czech_consonants = ur'bpdtgkzsZcvf\u010f\u0165hH\u017e\u0161\u017d\u010d'


czech_voiced_to_unvoiced_map = { u'b'  : u'p',
                                 u'd'  : u't',
                                 u'g'  : u'k',
                                 u'z'  : u's',
                                 u'Z'  : u'c',
                                 u'v'  : u'f',
                                 u'ď'  : u'ť',
                                 u'h'  : u'H',
                                 u'ž'  : u'š',
                                 u'Ž'  : u'č' }


czech_unvoiced_to_voiced_map = { u'p'  : u'b', 
                                 u't'  : u'd',
                                 u'k'  : u'g',
                                 u's'  : u'z',
                                 u'c'  : u'Z',
                                 u'f'  : u'v',
                                 u'ť'  : u'ď',
                                 u'H'  : u'h',
                                 u'š'  : u'ž',
                                 u'č'  : u'Ž' }


def debug_trace(str):
    if getConsoleVariableAsSwitch('a_devtrace'):
        msgW('FxAnalysis: [Czech Language Module]: ' + str)


def pronounce_czech_consonant_cluster(consonants):
    cluster = consonants.group(0)
    
    last_consonant = cluster[len(cluster) - 1]

    # Voiced v has no effect on the preceding consonants.
    if last_consonant == u'v':
        return cluster

    morphed = u''
      
    try:
        # If this doesn't raise a KeyError exception then we know the
        # last consonant in the cluster was voiced and we need to morph
        # all preceding unvoiced consonants into voiced consonants.
        czech_voiced_to_unvoiced_map[last_consonant]
            
        for u in cluster:
            try:
                morphed += czech_unvoiced_to_voiced_map[u]
            except KeyError:
                morphed += u

    except KeyError:
        pass

    try:
        # If this doesn't raise a KeyError exception then we know the
        # last consonant in the cluster was unvoiced and we need to morph
        # all preceding voiced consonants into unvoiced consonants.
        czech_unvoiced_to_voiced_map[last_consonant]
            
        for u in cluster:
            try:
                morphed += czech_voiced_to_unvoiced_map[u]
            except KeyError:
                morphed += u

    except KeyError:
        pass
      
    debug_trace('    morphing consonant cluster ' + cluster + ' -> ' + morphed)
      
    return morphed


def pronounce_czech_word(previous_word, current_word, next_word):
    pronunciation = []
    
    current_word = current_word.lower()
    original_word = current_word

    debug_trace('pronouncing ' + original_word)
    
    # Check for one letter prepositions that should voice or devoice based on the
    # first letter of the following word (preposisions are pronounced with the following
    # word and not standalone).
    if len(current_word) == 1 and len(next_word) > 0:
      next_word_lowercase = next_word.lower()
      if current_word == u'v' or current_word == u's' or current_word == u'z':
        # Run replacements on next_word_lowercase first.
        next_word_lowercase = next_word_lowercase.replace(u'ch', u'H')
        next_word_lowercase = next_word_lowercase.replace(u'dz', u'Z')
        next_word_lowercase = next_word_lowercase.replace(u'dž', u'Ž')
        # Now check for voicing or devoicing of the one letter preposition
        # based on the first letter of the next word.
        joined_word = current_word + next_word_lowercase
        # See the comments for this same line of code further down in the file for an
        # explanation of what it does.
        debug_trace('    joined: ' + joined_word)
        joined_word = re.sub(ur'([{0}]{{2,}})'.format(morphing_czech_consonants), pronounce_czech_consonant_cluster, joined_word)
        current_word = joined_word[0]
        debug_trace('    post: ' + current_word)

    # Replace ch with H for ease of lookup.
    current_word = current_word.replace(u'ch', u'H')
    
    # Replace certain vowel groups found in foreign words with uppercase letters
    # corresponding to the correct Czech pronunctiation for ease of lookup.
    current_word = current_word.replace(u'ia', u'A')
    current_word = current_word.replace(u'ie', u'E')
    current_word = current_word.replace(u'ii', u'I')
    current_word = current_word.replace(u'io', u'O')
    current_word = current_word.replace(u'iu', u'U')

    # Replace qu with kv.
    current_word = current_word.replace(u'qu', u'kv')

    # Expand q (remaining after qu replacement) and x.
    current_word = current_word.replace(u'q', u'kv')
    current_word = current_word.replace(u'x', u'ks')

    # Replace d' and t' with ď and ť.
    current_word = current_word.replace(u'd\'', u'ď')
    current_word = current_word.replace(u't\'', u'ť')

    # Exceptions.
    current_word = current_word.replace(u'oj', u'Y')
    current_word = current_word.replace(u'ej', u'#')
    current_word = current_word.replace(u'ěj', u'$')
    current_word = current_word.replace(u'uj', u'%')
    current_word = current_word.replace(u'új', u'%')
    current_word = current_word.replace(u'ůj', u'%')

    # Replace n with N when it precedes k or g. N maps to ŋ in czech_ipa_map.
    current_word = re.sub(ur'n([kg])', ur'N\1', current_word)

    # Replace d, t, and n when followed by i, í, or ě with ď, ť, and ň, respectively.
    # We have to use the \u syntax here because Python does not accept unicode characters
    # directly in regular expressions, hence the ur'\u' syntax.
    current_word = re.sub(ur'd([i\u00ed\u011b])', ur'\u010f\1', current_word)
    current_word = re.sub(ur't([i\u00ed\u011b])', ur'\u0165\1', current_word)
    current_word = re.sub(ur'n([i\u00ed\u011b])', ur'\u0148\1', current_word)

    # If the above replacement happend before ě, replace the ě with e so that
    # there is no double j pronunciation. E.g. dělám should be pronounced
    # as ɟɛlaːm and not ɟjɛlaːm (ignore that we use a instead of aː in our implementation).
    current_word = current_word.replace(u'ďě', u'ďe')
    current_word = current_word.replace(u'ťě', u'ťe')
    current_word = current_word.replace(u'ňě', u'ňe')

    # b, p, v, and f followed by ě are handled implicitly due to ě's pronunciation
    # definition in czech_ipa_table; but mě is pronounced mňe.
    current_word = current_word.replace(u'mě', u'mňe')

    # Temporarily replace dz and dž with Z and Ž, respectively, so that the following
    # assimilation rules are easier to implement.
    current_word = current_word.replace(u'dz', u'Z')
    current_word = current_word.replace(u'dž', u'Ž')

    # Convert the end of the word to unvoiced if applicable.
    if len(current_word) > 1:
        current_word = current_word[:-1] + czech_voiced_to_unvoiced_map.get(current_word[-1], current_word[-1])

    # Check for groups of two or more consonants. When such a group is found check
    # the last consonant in the group to see if it is voiced or unvoiced and 
    # morph the preceding consonants to match (e.g. they either all become voiced or
    # unvoiced depending on how the last consonant is classified).
    current_word = re.sub(ur'([{0}]{{2,}})'.format(morphing_czech_consonants), pronounce_czech_consonant_cluster, current_word)

    # Undo the dz and dž replacement if any are still present.
    current_word = current_word.replace(u'Z', u'dz')
    current_word = current_word.replace(u'Ž', u'dž')

    # Replace sh with sch (sH).
    current_word.replace(u'sh', u'sH')

    # Replace dz and dž with Z and Ž, respectively, for ease of lookup. This happens
    # at the end because rules above could prevent this from happening.
    current_word = current_word.replace(u'dz', u'Z')
    current_word = current_word.replace(u'dž', u'Ž')

    # Handle the ou dipthong which occurs in native Czech words.
    current_word = current_word.replace(u'ou', u'&')

    # Handle the dipthongs au and eu? I don't think it's necesssary for our facial animation
    # purposes since we'd split them out into their components again during coarticulation
    # anyway... plus it's a difficult problem because sometimes they are dipthongs and sometimes
    # they are not (e.g. at morpheme boundaries where there is a glottal stop). These two are only
    # found in foreign words or words of foreign origin. If it's a big deal on certain words their
    # pronunciation can always be overridden in the language dictionary.
    
    for c in current_word:
        try:
            ipa = czech_ipa_map[c]
            if isinstance(ipa, list):
                pronunciation.extend(ipa)
            else:
                pronunciation.append(ipa)
        except KeyError:
            errorW('Czech Language Pronouncer: {0} was not found in czech_ipa_map!'.format(c))
            raise
    
    pronunciation_string = u''
    for u in pronunciation:
        pronunciation_string += u
    
    debug_trace('result = ' + original_word + ' -> ' + pronunciation_string)
    
    return pronunciation

if __name__ == '__main__':
    registerLanguagePronouncer('Czech', 'ipa', pronounce_czech_word)
    msg('Czech Language Module registered.')

