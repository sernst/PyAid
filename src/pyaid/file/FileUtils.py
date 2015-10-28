# FileUtils.py
# (C)2011-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import sys
import gzip
import subprocess
import shutil
import mimetypes
from datetime import datetime
from collections import namedtuple

from pyaid.ArgsUtils import ArgsUtils
from pyaid.OsUtils import OsUtils
from pyaid.file.FileList import FileList
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils

#*******************************************************************************
class FileUtils(object):
    """ A convenience class that enhances system path related functionality.
    """

    WALK_DATA_NT = namedtuple('WALK_DATA_NT', [
        'rootPath', 'folder', 'names', 'data', 'files', 'folders'])

    #___________________________________________________________________________
    @classmethod
    def getFileExtension(cls, path):
        """ Retrieves the file extension for the specified path if an
            extension exists. If no file extension exists, or the path is not
            a file type, the method returns none.
        """
        if not path:
            return None
        if StringUtils.ends(path, os.path.sep):
            return None
        filename = path.split(os.path.sep)[-1]
        if not filename:
            return None
        parts = filename.split(os.path.extsep)
        if len(filename) < 2:
            return None
        return filename[-1]

    #___________________________________________________________________________
    @classmethod
    def makePathFromFile(cls, filePath, *args, **kwargs):
        """makePathFromFile doc..."""
        return cls.createPath(cls.getDirectoryOf(filePath), *args, **kwargs)

    #___________________________________________________________________________
    @classmethod
    def addToSysPath(cls, *args, **kwargs):
        """addToSysPath doc..."""
        path = cls.makeFolderPath(*args)
        if path not in sys.path:
            sys.path.append(path)

    #___________________________________________________________________________
    @classmethod
    def emptyFolder(cls, folderPath):
        """ Recursively empties all elements within a folder, and returns a
            boolean specifying whether the operation succeeded.
        """
        folderPath = cls.cleanupPath(folderPath, isDir=True)
        if not os.path.exists(folderPath):
            return False

        result = True
        for path in os.listdir(folderPath[:-1]):
            result = SystemUtils.remove(folderPath + path) and result
        return result

    #___________________________________________________________________________
    @classmethod
    def checkPathIsValid(cls, path, exists=True, writable =False):
        """checkPathIsValid doc..."""

        path   = cls.cleanupPath(path)
        parent = os.path.dirname(path)
        folder = parent if not os.path.isdir(path) else path

        if exists and not os.path.exists(parent) or not os.path.exists(path):
            return False, 'NO_PATH', 'No such path'

        if not os.access(folder, os.R_OK):
            return False, 'NO_READ', 'Read access denied'

        if writable and not os.access(folder, os.W_OK):
            return False, 'NO_WRITE', 'Write access denied'

        return True, 'VALID', 'Path is valid'

    #___________________________________________________________________________
    @classmethod
    def getPathToParentFolder(cls, path, parentFolderName, offset =0):
        """getPathToParentFolder doc..."""
        parts = path.strip(os.sep).split(os.sep)
        for i in range(len(parts)):
            if parts[i] == parentFolderName:
                parts = parts[:(i + 1 + offset)]
                if path.startswith(os.sep):
                    parts[0] = os.sep + parts[0]
                return FileUtils.createPath(*parts, isDir=True)
        return None

    #___________________________________________________________________________
    @classmethod
    def cleanFilename(cls, filename):
        if not filename:
            return StringUtils.getRandomString(12)
        out = StringUtils.slugify(filename)
        if not out:
            return StringUtils.getRandomString(12)
        return out

    #___________________________________________________________________________
    @classmethod
    def equivalentPaths(cls, path1, path2):
        path1 = FileUtils.cleanupPath(path1, noTail=True)
        path2 = FileUtils.cleanupPath(path2, noTail=True)
        return path1 == path2

    #___________________________________________________________________________
    @classmethod
    def isInFolder(cls, path, folder):
        if path.startswith(folder):
            return True

        test = FileUtils.createPath(folder, path.lstrip(os.sep))
        if os.path.exists(test):
            return True

    #___________________________________________________________________________
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
            return StringUtils.toUnicode(source)
        except Exception as err:
            if raiseErrors:
                raise
            print(err)
            return None

    #___________________________________________________________________________
    @classmethod
    def putContents(
            cls, content, path, append =False, raiseErrors =False,
            gzipped =False
    ):
        if not StringUtils.isStringType(content):
            content = ''
        content = StringUtils.toStr2(content)

        try:
            mode = 'a+' if append and os.path.exists(path) else 'w+'
            if gzipped:
                f = open(path, mode)
            else:
                f = open(path, mode)
            f.write(content)
            f.close()
        except Exception as err:
            if raiseErrors:
                raise
            print(err)
            return False

        return True

    #___________________________________________________________________________
    @classmethod
    def getModifiedDatetime(cls, path):
        if not os.path.exists(path):
            return None

        return datetime.fromtimestamp(os.path.getmtime(path))

    #___________________________________________________________________________
    @classmethod
    def getUTCModifiedDatetime(cls, path):
        if not os.path.exists(path):
            return None

        return datetime.utcfromtimestamp(os.path.getmtime(path))

    #___________________________________________________________________________
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
        except Exception:
            return False

        return True

    #___________________________________________________________________________
    @classmethod
    def getDirectoryOf(cls, path, createIfMissing =False, noTail =False):
        path = cls.cleanupPath(
            path=os.path.dirname(os.path.abspath(path)),
            noTail=noTail)
        if createIfMissing and not os.path.exists(path):
            os.makedirs(path)
        return path

    #___________________________________________________________________________
    @classmethod
    def getFilesOnPath(cls, rootPath, recursive =True, **kwargs):
        """ Returns a listing of the files (and directories if requested) for
            the given path as absolute or root-relative path elements as
            specified by the following arguments.

        :rootPath: string
            The highest level source path on which to list.

        :recursive: boolean
            When true the listing will contain entries for the root path and
            all sub directories on that path.

        :listFiles: boolean | True
            When true files get their own entry in the result. When false
            on directories are listed. Defaults to true.

        :listDirs: boolean | False
            When true directories get their own entry in the result. When
            false only files are listed. Defaults to false.

        :skipSVN: boolean | False
            When true entries for the .svn files are skipped.

        :skips:list
            An optional list of file and directory names to skip.

        :skipExtensions: list
            An optional list of file extensions to skip. All extensions not in
            the list are allowed.

        :allowExtensions: list | None
            An optional list of file extensions to include. All extensions not
            on the list are ignored.

        :allowDots: boolean | True
            When true, files and folders that begin with a dot (period) will
            be included. They ignored otherwise.

        :absolute: boolean | True
            When true the paths returned are absolute. When false the paths are
            returned relative to the root path as a slug, i.e. no leading slash
            separator.

        :pieces: boolean | False
            When true the paths are returned in folder pieces. The first piece
            if the absolute path to the root folder (if absolute is true) and
            subsequent pieces are the elements to the termainal path element.
        """

        if not os.path.exists(rootPath):
            return []

        return cls._listPath(rootPath, recursive, **kwargs)

    #___________________________________________________________________________
    @classmethod
    def getMimeType(cls, identifier, mimeType =None):
        """ Determines the enumerated type for the specified file.

        :identifier:string
            Either the file name, full path, or at least a file extension.
        """

        value = mimetypes.guess_type(
            mimeType, strict=False)[0] \
            if mimeType \
            else None
        if value:
            return value.lower()

        value = mimetypes.guess_type(identifier)[0]
        if value:
            return value.lower()

        return 'binary/octet-stream'

    #___________________________________________________________________________
    @classmethod
    def getExtensionByMimeType(mimeType):
        """Determines the extension based on the enumerated type."""

        if mimeType == 'image/jpeg':
            return '.jpg'
        else:
            return mimetypes.guess_extension(mimeType)

    #___________________________________________________________________________
    @classmethod
    def mergeCopy(cls, source, destination, overwriteExisting =True):
        """ Copies the source directory or file to the destination. Preserves
            the directories and files of the destination, but will overwrite
            any existing files with new ones if specified.

        :source: String
            Path to the source folder or file.

        :destination: String
            Path to the destination folder or file.

        :overwriteExisting: Boolean
            Specifies whether existing files should be overwritten by files
            copied from the source.
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
            cls.walkPath(source, cls._recursiveCopy, {
                'source':source,
                'destination':destination,
                'overwriteExisting':overwriteExisting,
                'fileList':fl })
        except Exception as err:
            return None

        return fl

    #___________________________________________________________________________
    @classmethod
    def makeFilePath(cls, *args, **kwargs):
        """createFilePath doc..."""
        kwargs['isFile'] = True
        return cls.createPath(*args, **kwargs)

    #___________________________________________________________________________
    @classmethod
    def makeFolderPath(cls, *args, **kwargs):
        """createFolderPath doc..."""
        kwargs['isDir'] = True
        return cls.createPath(*args, **kwargs)

    #___________________________________________________________________________
    @classmethod
    def createPath(cls, *args, **kwargs):
        """ Creates a system file path with the structure specified by the
            args arguments.
        """
        if not args:
            return None

        src = []
        for item in args:
            if not item:
                continue

            elif isinstance(item, list):
                src.extend(item)
            else:
                src.append(item)
        out = os.path.join(*src)

        noTail = kwargs.get('noTail', False)
        if kwargs.get('isFile', False):
            return cls._getAbsolutePath(out, noTail=False, isDir=False)

        if kwargs.get('isDir', False) or out.endswith(os.sep):
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

    #___________________________________________________________________________
    @classmethod
    def stripTail(cls, path):
        if path.endswith(os.sep):
            return path[:-1]
        return path

    #___________________________________________________________________________
    @classmethod
    def cleanupPath(cls, path, **kwargs):
        if not path:
            return path

        noTail = kwargs.get('noTail', False)
        path = cls._getAbsolutePath(path)

        if os.path.exists(path):
            if os.path.isdir(path):
                if noTail:
                    return path[:-1] if path.endswith(os.sep) else path
                return path + ('' if path.endswith(os.sep) else os.sep)
            return path

        if kwargs.get('isFile', False):
            if path.endswith(os.sep):
                return path[:-1]
            return path
        elif kwargs.get('isDir', False):
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

    #___________________________________________________________________________
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

    #___________________________________________________________________________
    @classmethod
    def generatePath(cls, *args, **kwargs):
        path = cls.createPath(*args, **kwargs)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    #___________________________________________________________________________
    @classmethod
    def walkPath(cls, rootPath, callback, data =None, recursive =True):
        """ Walks the specified root path, calling the specified callback in
            each folder recursively. The signature of the callback should be
            callback(walkData), a single argument that is an instance of
            FileUtils.WALK_DATA_NT.
        """

        for pathData in os.walk(rootPath):
            callback(cls.WALK_DATA_NT(
                rootPath=rootPath,
                folder=pathData[0],
                folders=pathData[1],
                files=pathData[2],
                names=pathData[1] + pathData[2],
                data=data ))

            # Break out after the first loop if not running in recursive mode
            if not recursive:
                return

    #___________________________________________________________________________
    @classmethod
    def openFolderInSystemDisplay(cls, path):
        """ Opens the specified folder (or the folder containing the specified
            file) in Explorer, Finder, or File Viewer depending on the platform.
        """
        if not os.path.exists(path):
            return False
        if not os.path.isdir(path):
            path = cls.getDirectoryOf(path)
        path = path.rstrip(os.sep)

        if OsUtils.isWindows():
            os.startfile(path)
            return True

        if OsUtils.isMac():
            os.system('open "%s"' % path)
            return True

        try:
            os.system('xdg-open "%s"' % path)
            return True
        except Exception as err:
            return False

    #===========================================================================
    #                                                         P R O T E C T E D

    #___________________________________________________________________________
    @classmethod
    def _getAbsolutePath(cls, path, noTail =False, isDir =False):
        outPath = os.path.abspath(path[:-1] if path.endswith(os.sep) else path)
        if not noTail and (isDir or path.endswith(os.sep)):
            return outPath + os.sep
        return outPath

    #___________________________________________________________________________
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

    #___________________________________________________________________________
    @classmethod
    def _recursiveCopy(cls, data):
        if data.folder in ['.svn']:
            return

        args        = data.data
        directory   = data.folder
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

        for item in data.files:
            srcPath  = os.path.join(directory, item)
            destPath = os.path.join(dest, item)
            if os.path.isfile(srcPath):
                cls._copyFile(srcPath, destPath, overwrite, fileList=fileList)

    #___________________________________________________________________________
    @classmethod
    def _listPath(cls, rootPath, recursive, **kwargs):
        allowDots       = kwargs.get('allowDots', True)
        rootPath        = cls.cleanupPath(rootPath, isDir=True)
        listFiles       = kwargs.get('listFiles', True)
        listDirs        = kwargs.get('listDirs', False)
        skipSVN         = kwargs.get('skipSVN', True)
        skips           = kwargs.get('skips', None)

        absolute        = kwargs.get('absolute', True)
        pieces          = kwargs.get('pieces', False)

        topPath         = ArgsUtils.extract('topPath', rootPath, kwargs)
        allowExtensions = ArgsUtils.getAsList('allowExtensions', kwargs)
        skipExtensions  = ArgsUtils.getAsList('skipExtensions', kwargs)

        out = []
        for item in os.listdir(rootPath):
            if not allowDots and item.startswith('.'):
                continue

            if (skipSVN and item == '.svn') or (skips and item in skips):
                continue

            absItem = os.path.join(rootPath, item)
            if os.path.isdir(absItem):
                path = absItem + os.sep
                if listDirs:
                    out.append(path if absolute else item)
                absItem = None

                if recursive:
                    out += cls._listPath(
                        rootPath=path,
                        recursive=recursive,
                        topPath=topPath, **kwargs)

            elif os.path.isfile(absItem):
                skip = skipExtensions and StringUtils.ends(item, skipExtensions)
                if not listFiles or skip:
                    continue

                if allowExtensions and not StringUtils.ends(item, allowExtensions):
                    continue

            if not absItem:
                continue

            if not pieces and not absolute:
                out.append(item)
                continue

            relativeItem = absItem[len(topPath):].strip(os.sep).split(os.sep)
            if absolute:
                relativeItem.insert(0, topPath)

            if pieces:
                out.append(relativeItem)
            else:
                out.append(os.path.join(*relativeItem))

        return out

