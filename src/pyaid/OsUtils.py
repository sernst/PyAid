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

    _WIN_DOCS_PATH = None

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

#___________________________________________________________________________________________________ getPerOsValue
    @classmethod
    def getPerOsValue(cls, windows =None, mac =None, linux =None):
        if cls.isWindows():
            return windows
        elif cls.isMac():
            return mac
        else:
            return linux

#___________________________________________________________________________________________________ getDocumentsPath
    @classmethod
    def getDocumentsPath(cls):
        if not cls.isWindows():
            return os.path.expanduser('~')

        if cls._WIN_DOCS_PATH:
            return cls._WIN_DOCS_PATH

        import ctypes.wintypes
        CSIDL_PERSONAL= 5       # My Documents
        SHGFP_TYPE_CURRENT= 0   # Want current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
        cls._WIN_DOCS_PATH = buf.value
        return cls._WIN_DOCS_PATH
