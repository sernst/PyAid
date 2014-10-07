# OsUtils.py
# (C)2013-2014
# Scott Ernst

import os
import sys
import re

# AS AVAILABLE: import AppKit
# AS AVAILABLE: import ctypes

# AS NEEDED: from pyaid.system.SystemUtils import SystemUtils

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

#___________________________________________________________________________________________________ isHighDpiScaledScreen
    @classmethod
    def isHighDpiScaledScreen(cls, index =-1):
        if cls.isMac():
            result = cls._getOsxDisplayInfo()
            if result['code'] or not 'out' in result:
                return None

            if index < 0:
                index = 0
            screenIndex = 0
            for line in result['out'].split(u'\n'):
                line = line.strip().lower()
                if not line.startswith('retina:'):
                    continue
                if screenIndex != index:
                    continue

                return line.split(':')[-1].strip().startswith('y')
            return True

        if cls.isWindows():
            return cls._getWindowsDpi() > 72.0

#___________________________________________________________________________________________________ getScreenResolution
    @classmethod
    def getScreenResolution(cls, index =-1):

        #-------------------------------------------------------------------------------------------
        if cls.isMac():
            try:
                import AppKit
                from AppKit import NSScreen

                if index == -1:
                    return int(NSScreen.mainScreen().frame().size.width), \
                           int(NSScreen.mainScreen().frame().size.height)

                i = 0
                for screen in AppKit.NSScreen.screens():
                    if i != index:
                        continue
                    return screen.frame().size.width, screen.frame().size.height
                return None
            except Exception, err:
                pass

            result = cls._getOsxDisplayInfo()
            if result['code'] or not 'out' in result:
                return None

            if index < 0:
                index = 0
            screenIndex = 0
            for line in result['out'].split(u'\n'):
                line = line.strip().lower()
                if not line.startswith('resolution:'):
                    continue
                if screenIndex != index:
                    continue

                result = re.search(r'(?P<width>[0-9]{3,})[^0-9]+(?P<height>[0-9]{3,})', line)
                return int(result.group('width')), int(result.group('height'))
            return None

        #-------------------------------------------------------------------------------------------
        if cls.isWindows():
            try:
                import ctypes
            except Exception, err:
                return None
            user32 = ctypes.windll.user32
            return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getOsxDisplayInfo
    @classmethod
    def _getOsxDisplayInfo(cls):
        from pyaid.system.SystemUtils import SystemUtils
        return SystemUtils.executeCommand(['system_profiler', 'SPDisplaysDataType'])

#___________________________________________________________________________________________________ _getWindowsDpi
    @classmethod
    def _getWindowsDpi(cls):
        from pyaid.system.SystemUtils import SystemUtils
        result = SystemUtils.executeCommand([
            'wmic', 'DesktopMonitor', 'Get', 'PixelsPerXLogicalInch, PixelsPerYLogicalInch'])
        if result['code'] or not 'out' in result:
            return 72.0

        data = result['out'].replace('\r', '').strip().split('\n')[-1].strip()
        if not data:
            return 72.0

        if data.find(' ') == -1:
            return float(data)

        data = re.sub(r'\s{2,}', ' ', data).split(' ')
        return float(data[0])


