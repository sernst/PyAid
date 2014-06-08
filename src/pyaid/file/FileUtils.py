# FileUtils.py
# (C)2011-2013
# Scott Ernst

from __future__ import absolute_import
import os
import sys
import gzip
import subprocess
import shutil
import mimetypes
from datetime import datetime
from collections import namedtuple

from pyaid.ArgsUtils import ArgsUtils
from pyaid.file.FileList import FileList
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ FileUtils
class FileUtils(object):
    """A class for..."""

    WALK_DATA_NT = namedtuple('WALK_DATA_NT', ['rootPath', 'folder', 'names', 'data'])

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ equivalentPaths
    @classmethod
    def equivalentPaths(cls, path1, path2):
        path1 = FileUtils.cleanupPath(path1, noTail=True)
        path2 = FileUtils.cleanupPath(path2, noTail=True)
        return path1 == path2

#___________________________________________________________________________________________________ isInFolder
    @classmethod
    def isInFolder(cls, path, folder):
        if path.startswith(folder):
            return True

        test = FileUtils.createPath(folder, path.lstrip(os.sep))
        if os.path.exists(test):
            return True

#___________________________________________________________________________________________________ getContents
    @classmethod
    def getContents(cls, path, raiseErrors =False, gzipped =False):
        if not os.path.exists(path):
            return None
        try:
            if gzipped:
                f = gzip.open(path, 'r+')
            else:
                f = open(path, 'r+')
            source = f.read()
            f.close()
            return source.decode('utf-8', 'ignore')
        except Exception, err:
            if raiseErrors:
                raise
            print err
            return None

#___________________________________________________________________________________________________ putContents
    @classmethod
    def putContents(cls, content, path, append =False, raiseErrors =False, gzipped =False):
        if not isinstance(content, basestring):
            content = u''
        elif isinstance(content, unicode):
            try:
                content = content.encode('utf-8', 'ignore')
            except Exception, err:
                if raiseErrors:
                    raise
                print err
                return False

        try:
            mode = 'a+' if append and os.path.exists(path) else 'w+'
            if gzipped:
                f = open(path, mode)
            else:
                f = open(path, mode)
            f.write(content)
            f.close()
        except Exception, err:
            if raiseErrors:
                raise
            print err
            return False

        return True

#___________________________________________________________________________________________________ getModifiedDatetime
    @classmethod
    def getModifiedDatetime(cls, path):
        if not os.path.exists(path):
            return None

        return datetime.fromtimestamp(os.path.getmtime(path))

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

#___________________________________________________________________________________________________ getDirectoryOf
    @classmethod
    def getDirectoryOf(cls, path, createIfMissing =False):
        path = os.path.dirname(os.path.abspath(path))
        if createIfMissing and not os.path.exists(path):
            os.makedirs(path)
        return path

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

        value = mimetypes.guess_type(mimeType, strict=False)[0] if mimeType else None
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
            cls._copyFile(source, destination, overwriteExisting, fileList=fl)
            return fl

        if not source.endswith(os.sep):
            source += os.sep

        if not destination.endswith(os.sep):
            destination += os.sep

        try:
            os.path.walk(source, cls._recursiveCopy, {
                'source':source,
                'destination':destination,
                'overwriteExisting':overwriteExisting,
                'fileList':fl })
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

        noTail = ArgsUtils.get('noTail', False, kwargs)
        if ArgsUtils.get('isFile', False, kwargs):
            return cls._getAbsolutePath(out, noTail=False, isDir=False)

        if ArgsUtils.get('isDir', False, kwargs) or out.endswith(os.sep):
            return cls._getAbsolutePath(out, noTail=noTail, isDir=True)

        if os.path.exists(out):
            if os.path.isfile(out):
                return cls._getAbsolutePath(out, noTail=True, isDir=False)

            if os.path.isdir(out) and not noTail and not out.endswith(os.sep):
                out += os.sep
        elif out.endswith('..'):
            out += os.sep
        elif src[-1].find('.') == -1:
            out += os.sep

        return cls._getAbsolutePath(out, noTail=noTail)

#___________________________________________________________________________________________________ stripTail
    @classmethod
    def stripTail(cls, path):
        if path.endswith(os.sep):
            return path[:-1]
        return path

#___________________________________________________________________________________________________ cleanupPath
    @classmethod
    def cleanupPath(cls, path, **kwargs):
        if not path:
            return path

        noTail = ArgsUtils.get('noTail', False, kwargs)
        path = cls._getAbsolutePath(path)

        if os.path.exists(path):
            if os.path.isdir(path):
                if noTail:
                    return path[:-1] if path.endswith(os.sep) else path
                return path + (u'' if path.endswith(os.sep) else os.sep)
            return path

        if ArgsUtils.get('isFile', False, kwargs):
            if path.endswith(os.sep):
                return path[:-1]
            return path
        elif ArgsUtils.get('isDir', False, kwargs):
            if noTail:
                if path.endswith(os.sep):
                    path = path[:-1]
            elif not path.endswith(os.sep):
                path += os.sep
        else:
            if path.endswith(os.sep):
                return path[:-1] if noTail else path

            if not noTail:
                sepIndex = path.rfind(os.sep)
                extIndex = path.rfind('.')
                if extIndex < sepIndex:
                    path += os.sep

        return path

#___________________________________________________________________________________________________ changePathRoot
    @classmethod
    def changePathRoot(cls, path, oldRootPath, newRootPath):
        path = cls.cleanupPath(path)
        oldRootPath = cls.cleanupPath(oldRootPath, isDir=True)
        newRootPath = cls.cleanupPath(newRootPath, isDir=True)

        if path == oldRootPath:
            return newRootPath

        if not path.startswith(oldRootPath):
            return None

        return newRootPath + path[len(oldRootPath):]

#___________________________________________________________________________________________________ generatePath
    @classmethod
    def generatePath(cls, *args, **kwargs):
        path = cls.createPath(*args, **kwargs)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

#___________________________________________________________________________________________________ walkPath
    @classmethod
    def walkPath(cls, rootPath, callback, data =None):
        """ Walks the specified root path, calling the specified callback in each folder
            recursively. The signature of the callback should be callback(walkData), a single
            argument that is an instance of FileUtils.WALK_DATA_NT. """

        os.path.walk(rootPath, cls._handleWalkPath, {
            'rootPath':rootPath,
            'callback':callback,
            'data':data })

#___________________________________________________________________________________________________ createWalkData
    @classmethod
    def createWalkData(cls, rootPath =None, folder =None, names =None, data =None):
        return cls.WALK_DATA_NT(rootPath, folder, names, data)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getAbsolutePath
    @classmethod
    def _getAbsolutePath(cls, path, noTail =False, isDir =False):
        outPath = os.path.abspath(path[:-1] if path.endswith(os.sep) else path)
        if not noTail and (isDir or path.endswith(os.sep)):
            return outPath + os.sep
        return outPath

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

        directory   = cls.cleanupPath(directory, isDir=True)
        source      = cls.cleanupPath(args['source'], isDir=True)
        destination = cls.cleanupPath(args['destination'], isDir=True)
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

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleWalkPath
    @classmethod
    def _handleWalkPath(cls, args, dirname, names):
            args['callback'](cls.createWalkData(
                rootPath=args['rootPath'],
                folder=dirname,
                names=names,
                data=args['data'] ))
