# This module is automatically imported by Python's built-in site.py module during
# Python initialization.  This is here to set the default encoding to utf-8.  This is so that 
# writing scripts in FaceFX doesn't involve enoding unicode strings which can be confusing 
# to artists.  For example:
#
# print phoneme.encode('utf-8')
#
# vs.
#
# print phoneme

import sys
sys.setdefaultencoding('utf-8')
