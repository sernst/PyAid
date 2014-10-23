# SystemCommandIssuer.py
# (C)2012-2013
# Scott Ernst

import os

from pyaid.file.FileUtils import FileUtils
from pyaid.system.SystemUtils import SystemUtils

#___________________________________________________________________________________________________ SystemCommandIssuer
class SystemCommandIssuer(object):
    """A base class for server classes that issue external commands."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, raiseExceptions =True, *args, **kwargs):
        """Creates a new instance of SystemCommandIssuer."""
        self._raiseCommandExceptions = raiseExceptions
        self._commandIndex           = 0

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: currentDirectory
    @property
    def currentDirectory(self):
        return os.getcwd()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _download
    def _download(self, url, target, httpsVerify =False, critical =None):
        print 'Downloading %s -> %s' % (url, target)
        try:
            result = SystemUtils.download(
                url=url,
                target=target,
                httpsVerify=httpsVerify,
                critical=critical,
                raiseExceptions=self._raiseCommandExceptions)
        except Exception, err:
            print 'DOWNLOAD FAILED\n', err
            if critical or (critical is None and self._raiseCommandExceptions):
                raise err
            else:
                print err
                return False

        if not result:
            if critical or (critical is None and self._raiseCommandExceptions):
                raise Exception, 'Download failed'
            else:
                print 'DOWNLOAD FAILED'
                return False

        print 'SUCCESS'
        return True

#___________________________________________________________________________________________________ _getOutput
    def _getOutput(self, cmd, critical =None):
        self._commandIndex += 1
        print '\n[%s EXECUTE<OUTPUT>]: %s' % (str(self._commandIndex), cmd)
        try:
            out = SystemUtils.executeForOutput(cmd, critical=critical)
        except Exception, err:
            print 'FAILED'
            if critical or (critical is None and self._raiseCommandExceptions):
                raise err
            return None

        print 'SUCCESS'
        return out

#___________________________________________________________________________________________________ _run
    def _run(self, cmd, critical =None):
        self._commandIndex  += 1
        print '\n[%s EXECUTE]: %s' % (str(self._commandIndex), cmd)
        stat = SystemUtils.executeForStatus(cmd, critical=critical)
        if not stat:
            print 'SUCCESS'
        else:
            print 'FAILED'

        if not stat:
            if critical or (critical is None and self._raiseCommandExceptions):
                raise Exception, 'Command execution failed with status: %s' % stat
            else:
                return False

        return True

#___________________________________________________________________________________________________ _createPath
    def _createPath(self, path):
        if os.path.exists(path):
            print 'PATH ALREADY EXISTS: ' + path
            return None

        path = FileUtils.generatePath(path)
        print 'CREATED PATH: ' + path
        return path

#___________________________________________________________________________________________________ _copy
    def _copy(self, source, destination):
        result = SystemUtils.copy(source, destination)
        if not result:
            print 'FAILED TO COPY: %s -> %s' % (source, destination)
            return False

        print 'COPIED: %s -> %s' % (source, destination)
        return True

#___________________________________________________________________________________________________ _gzip
    def _gzip(self, target):
        return SystemUtils.gzip(target)

#___________________________________________________________________________________________________ _ungzip
    def _ungzip(self, target):
        return SystemUtils.ungzip(target)

#___________________________________________________________________________________________________ _tar
    def _tar(self, zipTarget, fileList, append =False, newerOnly =False, gzip =True):
        out = SystemUtils.tar(
            zipTarget=zipTarget,
            fileList=fileList,
            append=append,
            newerOnly=newerOnly,
            gzip=gzip)

        if out is None:
            print 'FAILED TO TAR: ' + str(zipTarget)
            return None

        print 'TARRED: ' + str(zipTarget)
        return out

#___________________________________________________________________________________________________ _untar
    def _untar(self, zipSource, overwriteAll =True, gzip =None):
        result = SystemUtils.untar(
            zipSource=zipSource,
            overwriteAll=overwriteAll,
            gzip=gzip)

        if not result:
            print 'FAILED TO UNTAR: ' + str(zipSource)
            return False

        print 'UNTARRED: ' + str(zipSource)
        return True

#___________________________________________________________________________________________________ _7zip
    def _7zip(self, zipTarget, fileList, append =False):
        """Don't use 7zip except for isolated files. It's not recursive."""
        result = SystemUtils.do7zip(zipTarget=zipTarget, fileList=fileList, append=append)

        if not result:
            print 'FAILED TO ZIP: ' + str(zipTarget)
            return False

        print 'ZIPPED: ' + str(zipTarget)
        return True

#___________________________________________________________________________________________________ _un7zip
    def _un7zip(self, zipSource, targetPath =None, overwriteAll =True):
        result = SystemUtils.un7zip(
            zipSource=zipSource,
            targetPath=targetPath,
            overwriteAll=overwriteAll)

        if not result:
            print 'FAILED TO UN7ZIP: ' + str(zipSource)
            return False

        print 'UN7ZIPPED: ' + str(zipSource)
        return True

#___________________________________________________________________________________________________ _move
    def _move(self, source, destination):
        if not SystemUtils.move(source, destination):
            print 'FAILED TO MOVE: %s -> %s' % (source, destination)
            return False

        print 'MOVED: %s -> %s' % (source, destination)
        return True

#___________________________________________________________________________________________________ _remove
    def _remove(self, path):
        if not os.path.exists(path):
            print 'NOTHING TO REMOVE: ' + path
            return False

        result = SystemUtils.remove(path)
        if not result:
            print 'FAILED TO REMOVE: ' + path
            return False

        print 'REMOVED PATH: ' + path
        return True

#___________________________________________________________________________________________________ _findMatchingDir
    def _findMatchingDir(self, pattern, path =None):
        return SystemUtils.findMatchingDir(pattern, path)

#___________________________________________________________________________________________________ _changePermissions
    def _changePermissions(
            self, permissions ='777', path =None, owner =None, group =None, recursive =True
    ):
        return SystemUtils.changePermissions(
            permissions=permissions,
            path=path,
            owner=owner,
            group=group,
            recursive=recursive)

#___________________________________________________________________________________________________ _changeDir
    def _changeDir(self, path):
        os.chdir(path)
        print 'CURRENT DIRECTORY: %s [%s]' % (os.curdir, path)

#___________________________________________________________________________________________________ _listDir
    def _listDir(self, path =None, dirs =True, files =True, absolute =True):
        return SystemUtils.listDir(path=path, dirs=dirs, files=file, absolute=absolute)
