""" This module provides utility functions for FaceFX python scripting that
needed a good home.

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio


def isConsoleVariableSetToDefault(cvarName):
    """ Returns True if the given console variable is currently set to its
    default value and False otherwise.
    """
    return FxStudio.getConsoleVariable(cvarName) == \
        FxStudio.getConsoleVariableDefault(cvarName)
