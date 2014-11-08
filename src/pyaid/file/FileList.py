# FileList.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from pyaid.list.ListUtils import ListUtils
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ FileList
class FileList(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    CREATED  = 'created'
    MODIFIED = 'modified'
    REMOVED  = 'removed'

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of FileList."""
        self._index       = 0
        self._files       = dict()
        self._directories = dict()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: files
    @property
    def files(self):
        return self._files

#___________________________________________________________________________________________________ GS: directories
    @property
    def directories(self):
        return self._directories

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ removeAll
    def removeAll(self, flags, files =True, directories =True):
        return self.removeFiltered(None, files=files, directories=directories)

#___________________________________________________________________________________________________ removeFiltered
    def removeFiltered(self, flags, files =True, directories =True):
        removes = self.getFilteredByFlags(flags)
        for item in removes:
            if not os.path.exists(item):
                continue

            try:
                if os.path.isdir(item) and directories:
                    os.removedirs(item)
                elif files:
                    os.remove(item)
            except Exception:
                print('FileUtils copy failure:')
                print('\tITEM: ' + str(item))
                print('\tITEMS: ' + str(item))
                raise

        return True

#___________________________________________________________________________________________________ getFilteredByFlags
    def getFilteredByFlags(self, flags, files =True, directories =True):
        if StringUtils.isStringType(flags):
            flags = [flags]

        sources = []
        if directories:
            sources += self._directories.values()
        if files:
            sources += self._files.values()

        sources.sort(key=lambda x:x['index'])

        out = []
        for src in sources:
            if flags is None or ListUtils.contains(src['flags'], flags):
                out.insert(0, src['item'])

        return out

#___________________________________________________________________________________________________ addFile
    def addFile(self, name, path =None, flags =None):
        """Doc..."""
        item = self._getFullPath(name, path, False)
        self._files[item] = {'index':self._index, 'flags':flags, 'item':item}
        self._index += 1
        return True

#___________________________________________________________________________________________________ removeFile
    def removeFile(self, name, path =None, flags =None):
        """Doc..."""
        item = self._getFullPath(name, path, False)
        if item in self._files:
            del self._files[item]
            return True
        return False

#___________________________________________________________________________________________________ addDirectory
    def addDirectory(self, name, path =None, flags =None):
        """Doc..."""
        item = self._getFullPath(name, path, True)
        self._directories[item] = {'index':self._index, 'flags':flags, 'item':item}
        self._index += 1
        return True

#___________________________________________________________________________________________________ removeDirectory
    def removeDirectory(self, name, path =None, flags =None):
        """Doc..."""
        item = self._getFullPath(name, path, True)
        if item in self._directories:
            del self._directories[item]
            return True
        return False

#___________________________________________________________________________________________________ createFromRootPath
    @classmethod
    def createFromRootPath(cls, path =None, flags =None):
        out = FileList()

        if not flags:
            flags = []
        elif StringUtils.isStringType(flags):
            flags = [flags]

        os.path.walk(path, cls._rootPathWalker, {
            'rootPath':path,
            'out':out,
            'flags':flags })
        return out

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getFullPath
    def _getFullPath(self, name, path, isDir):
        """Doc..."""
        return os.path.join(path, name) if path else name + (os.sep if isDir else '')

#___________________________________________________________________________________________________ _rootPathWalker
    @classmethod
    def _rootPathWalker(cls, args, directory, items):
        commonFlags = args['flags']

        args['out'].addDirectory(directory, path=args['rootPath'], flags=([] + commonFlags))

        path = os.path.join(args['rootPath'], directory)
        for item in items:
            itemPath = os.path.join(path, item)
            if os.path.isfile(itemPath):
                args['out'].addFile(item, path=path, flags=([] + commonFlags))

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

