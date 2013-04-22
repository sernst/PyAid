# FileUtils.py
# (C)2011-2013
# Scott Ernst

import os
import sys
import subprocess
import shutil
import mimetypes
from datetime import datetime

from pyaid.ArgsUtils import ArgsUtils
from pyaid.file.FileList import FileList
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ FileUtils
class FileUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getUTCModifiedTime
    @classmethod
    def getUTCModifiedDatetime(cls, path):
        if not os.path.exists(path):
            return None

        return datetime.utcfromtimestamp(os.path.getmtime(path))

#___________________________________________________________________________________________________ exploreLocation
    @classmethod
    def exploreLocation(cls, target):
        if not os.path.exists(target):
            return False

        try:
            if sys.platform == 'windows':
                subprocess.check_call(['explorer', target])
            elif sys.platform.lower().find('linux'):
                subprocess.check_call(['gnome-open', '--', target])
            else:
                subprocess.call(["open", "-R", target])
        except Exception, err:
            return False

        return True

#___________________________________________________________________________________________________ getFilesOnPath
    @classmethod
    def getFilesOnPath(cls, rootPath, recursive =True, **kwargs):
        """ Returns a listing of the files (and directories is requested) for the given path as
            absolute path elements.

            @@@param rootPath:string
                The highest level source path on which to list.

            @@@param recursive:boolean
                When true the listing will contain entries for the root path and all sub directories
                on that path.

            @@@param listDirs:boolean
                When true directories get their own entry in the result. When false only files are
                listed.

            @@@param skipSVN:boolean
                When true entries for the .svn files are skipped.

            @@@param skips:list
                An optional list of file and directory names to skip.

            @@@param skipExtensions:list
                An optional list of file extensions to skip. All extensions not in the list are
                allowed.

            @@@param allowExtensions:list
                An optional list of file extensions to include. All extensions not on the list
                are ignored.
        """

        return cls._listPath(rootPath, recursive, **kwargs)

#___________________________________________________________________________________________________ getMimeType
    @staticmethod
    def getMimeType(identifier, mimeType =None):
        """Determines the enumerated type for the specified file.

        @@@param identifier:string
            Either the file name, full path, or at least a file extension.
        """

        value = mimetypes.guess_type(mimeType)[0] if mimeType else None
        if value:
            return value.lower()

        value = mimetypes.guess_type(identifier)[0]
        if value:
            return value.lower()

        return 'binary/octet-stream'

#___________________________________________________________________________________________________ getExtensionByMimeType
    @staticmethod
    def getExtensionByMimeType(mimeType):
        """Determines the extension based on the enumerated type."""

        if mimeType == 'image/jpeg':
            return '.jpg'
        else:
            return mimetypes.guess_extension(mimeType)

#___________________________________________________________________________________________________ mergeCopy
    @classmethod
    def mergeCopy(cls, source, destination, overwriteExisting =True):
        """ Copies the source directory or file to the destination. Preserves the directories and
            files of the destination, but will overwrite any existing files with new ones if
            specified.

            @@@param source:String
                Path to the source folder or file.

            @@@param destination:String
                Path to the destination folder or file.

            @@@param overwriteExisting:Boolean
                Specifies whether existing files should be overwritten by files copied from
                the source.
        """

        if not os.path.exists(source):
            return None

        fl = FileList()

        if os.path.isfile(source):
            return cls._copyFile(source, destination, overwriteExisting, fileList=fl)

        if not source.endswith(os.sep):
            source += os.sep

        if not destination.endswith(os.sep):
            destination += os.sep

        try:
            os.path.walk(source, cls._recursiveCopy, {
                'source':source,
                'destination':destination,
                'overwriteExisting':overwriteExisting,
                'fileList':fl
            })
        except Exception, err:
            return None

        return fl

#___________________________________________________________________________________________________ createPath
    @classmethod
    def createPath(cls, *args, **kwargs):
        """Doc..."""
        if not args or args[0] is None:
            return None

        src = []
        for item in args:
            if isinstance(item, list):
                src.extend(item)
            else:
                src.append(item)
        out = os.path.join(*src)

        if out.endswith(os.sep) or ArgsUtils.get('isFile', False, kwargs):
            return cls._getAbsolutePath(out)

        if ArgsUtils.get('isDir', False, kwargs):
            return cls._getAbsolutePath(out) + os.sep

        if os.path.exists(out):
            if os.path.isfile(out):
                return cls._getAbsolutePath(out)

            if os.path.isdir(out) and not out.endswith(os.sep):
                out += os.sep
        elif out.endswith('..'):
            out += os.sep
        elif src[-1].find('.') == -1:
            out += os.sep

        return cls._getAbsolutePath(out)

#___________________________________________________________________________________________________ cleanupPath
    @classmethod
    def cleanupPath(cls, path, **kwargs):
        if os.path.exists(path):
            if os.path.isdir(path) and not path.endswith(os.sep):
                return cls._getAbsolutePath(path) + os.sep
            return cls._getAbsolutePath(path)

        if ArgsUtils.get('isFile', False, kwargs):
            if path.endswith(os.sep):
                return cls._getAbsolutePath(path[:-1])
            return cls._getAbsolutePath(path)
        elif ArgsUtils.get('isDir', False, kwargs):
            if not path.endswith(os.sep):
                path += os.sep
        else:
            sepIndex = path.rfind(os.sep)
            extIndex = path.rfind('.')
            if extIndex < sepIndex and not path.endswith(os.sep):
                path += os.sep

        return cls._getAbsolutePath(path)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getAbsolutePath
    @classmethod
    def _getAbsolutePath(cls, path):
        if path.endswith(os.sep):
            return os.path.abspath(path[:-1]) + os.sep
        return os.path.abspath(path)

#___________________________________________________________________________________________________ _copyFile
    @classmethod
    def _copyFile(cls, source, destination, overwrite =True, fileList =None):
        flag = FileList.CREATED
        if os.path.exists(destination) and os.path.isfile(destination):
            if not overwrite:
                return True
            os.remove(destination)
            flag = FileList.MODIFIED

        fileList.addFile(destination, flags=flag)
        shutil.copy2(source, destination)

        return True

#___________________________________________________________________________________________________ _recursiveCopy
    @classmethod
    def _recursiveCopy(cls, args, directory, items):
        if directory in ['.svn']:
            return

        source      = args['source']
        destination = args['destination']
        overwrite   = args['overwriteExisting']
        fileList    = args['fileList']

        if directory == source or len(directory) <= len(source):
            dest = destination
        else:
            dest = os.path.join(destination, directory[len(source):])
        if not os.path.exists(dest):
            fileList.addDirectory(dest, flags=FileList.CREATED)
            os.makedirs(dest)

        for item in items:
            srcPath  = os.path.join(directory, item)
            destPath = os.path.join(dest, item)
            if os.path.isfile(srcPath):
                cls._copyFile(srcPath, destPath, overwrite, fileList=fileList)

#___________________________________________________________________________________________________ _listPath
    @classmethod
    def _listPath(cls, rootPath, recursive, **kwargs):
        listDirs        = ArgsUtils.get('listDirs', False, kwargs)
        skipSVN         = ArgsUtils.get('skipSVN', True, kwargs)
        skips           = ArgsUtils.get('skips', None, kwargs)
        allowExtensions = ArgsUtils.getAsList('allowExtensions', kwargs)
        skipExtensions  = ArgsUtils.getAsList('skipExtensions', kwargs)

        out = []
        for item in os.listdir(rootPath):
            if (skipSVN and item == '.svn') or (skips and item in skips):
                continue
            absItem = os.path.join(rootPath, item)
            if os.path.isdir(absItem):
                path = (absItem + os.sep)
                if listDirs:
                    out.append(path)
                absItem = None

                if recursive:
                    out += cls._listPath(path, recursive, **kwargs)

            elif os.path.isfile(absItem):
                if skipExtensions and StringUtils.ends(item, skipExtensions):
                    continue

                if allowExtensions and not StringUtils.ends(item, allowExtensions):
                    continue

            if absItem:
                out.append(absItem)

        return out
