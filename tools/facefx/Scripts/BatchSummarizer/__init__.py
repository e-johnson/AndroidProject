""" Batch summarizer plugin definition.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import BatchSummarizer
import FxStudio


_BATCHSUMMARY_VERSION = '1.0'
_BATCHSUMMARY_AUTHOR = 'OC3 Entertainment'
_BATCHSUMMARY_DESC = 'Prints a summary of batch analysis operations.'


def info():
    """ Return the tuple with information about the plugin.

    This is a __facefx__ native plugin, meaning it will default to being
    loaded on a fresh install of FaceFX Studio.

    """
    return (_BATCHSUMMARY_VERSION, _BATCHSUMMARY_AUTHOR, _BATCHSUMMARY_DESC)


def load():
    """ Load the plugin by connecting it to the log output stream.

    """
    FxStudio.connectSignal('messagelogged', BatchSummarizer.on_log_message)


def unload():
    """ Unload the plugin by disconnecting it from the log output stream.

    """
    FxStudio.disconnectSignal('messagelogged', BatchSummarizer.on_log_message)
