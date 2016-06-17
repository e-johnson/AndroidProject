"""
A library of helper functions useful while scripting FaceFX Studio.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import FxStudio
from base64 import b64encode
from math import exp


class Progress(object):
    """ Wraps FaceFX Studio's progress display in a class to be used in a
    Python "with" statement.

    This class will ensure the progress display is properly ended for any
    execution path, preventing potential hangs. Also exposes a handy 'update'
    function so developers need not look up the actual Studio command to update
    the progress display.

    For example:
    >>> with Progress("working on a long task...") as progress:
    ...     # some statements that take a long time.
    ...     progress.update(0.5)
    ...     # some more long-running statements
    ...     progress.update(0.9)
    ... # progress dialog will automatically dismiss once out of "with" scope.

    """
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        FxStudio.beginProgressDisplay(self.msg)
        return self

    def __exit__(self, type, value, traceback):
        FxStudio.endProgressDisplay()

    def update(self, pct):
        """ Updates the percentage complete to pct """
        set_overall_progress(pct)

    def get_percentage_complete(self):
        """ Returns the percentage complete. """
        return get_overall_progress()


class Unattended(object):
    """ Wraps FaceFX Studio's unattended setting in a class to be used in
    a Python "with" statement.

    This class will ensure the unattended setting is properly reset for any
    execution path.

    """
    def __init__(self):
        self.old_setting = FxStudio.getConsoleVariable('g_unattended')

    def __enter__(self):
        FxStudio.setConsoleVariable('g_unattended', 1)
        return self

    def __exit__(self, type, value, traceback):
        FxStudio.setConsoleVariable('g_unattended', self.old_setting)


def get_selected_animpath():
    """ Return the selected animation's path in the form 'group/anim'. """
    return '{0}/{1}'.format(FxStudio.getSelectedAnimGroupName(),
        FxStudio.getSelectedAnimName())


def split_animpath(animpath):
    """ Splits 'group/anim' and returns ('group', 'anim'). """
    animGroupName, sep, animName = animpath.partition('/')
    return (animGroupName, animName)


def anim_exists(animpath):
    """ Returns true if the animation exists in the actor. """
    try:
        FxStudio.getAnimationProperties(*split_animpath(animpath))
        return True
    except RuntimeError:
        return False


def group_exists(group):
    """ Returns true if the animation group exists in the actor. """
    return group in set([x[0] for x in FxStudio.getAnimationNames()])


def group_to_word(start_index, end_index, word_text):
    """ Issues a FaceFX Studio command to group the phonemes to a word. """
    try:
        ascii_text = word_text.decode('ascii')
    except UnicodeDecodeError:
        encodedWord = b64encode(word_text.encode('utf-8'))
        word_command = '-wordTextUnicode "{0}"'.format(encodedWord)
    else:
        word_command = '-wordText "{0}"'.format(ascii_text)
    FxStudio.issueCommand('phonList -group -startIndex "{0}" -endIndex "{1}" '
        '{2}'.format(start_index, end_index, word_command))


def set_overall_progress(overall_progress):
    """ Sets the overall progress of the task. """
    FxStudio.setConsoleVariableFast('pp_overall_progress', overall_progress)


def get_overall_progress():
    """ Returns the overall progress of the task. """
    return float(FxStudio.getConsoleVariable('pp_overall_progress'))


def set_task_name(task_name):
    """ Sets the progress bar task name. """
    FxStudio.setConsoleVariableFast('pp_task_name', task_name)


def set_task_progress(task_progress):
    """ Sets the progress bar task progress. """
    FxStudio.setConsoleVariableFast('pp_task_progress', task_progress)


def estimate_percentile(sample, mean, std_dev):
    """ Estimates the percentile of a sample based on the population. """
    z_score = (sample - mean) / std_dev
    return 1 / (1 + exp(-1.7 * z_score))
