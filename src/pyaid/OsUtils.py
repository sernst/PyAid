# OsUtils.py
# (C)2013
# Scott Ernst

import os
import sys

#___________________________________________________________________________________________________ OsUtils
class OsUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ isWindows
    @classmethod
    def isWindows(cls):
        return sys.platform.startswith('win')

#___________________________________________________________________________________________________ isMac
    @classmethod
    def isMac(cls):
        return sys.platform == 'darwin'

#___________________________________________________________________________________________________ firstExisting
    @classmethod
    def firstExisting(cls, *args):
        for item in args:
            if os.path.exists(item):
                return item
        return None
