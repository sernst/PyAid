# SystemUtils.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import re
import os
import shutil
import datetime
import subprocess

# AS NEEDED: import urllib2
# AS NEEDED: import requests
# AS NEEDED: from pyaid.list.ListUtils import ListUtils

if sys.version > '3':
    from urllib import request
    urlopen = request.urlopen
else:
    import urllib2
    urlopen = urllib2.urlopen

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ SystemUtils
class SystemUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ executeCommand
    @classmethod
    def executeCommand(cls, cmd, remote =False, shell =True, wait =False):
        if shell and not StringUtils.isStringType(cmd):
            from pyaid.list.ListUtils import ListUtils
            cmd = ' '.join(ListUtils.itemsToString(cmd))

        if remote:
            pipe = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=None,
                stderr=None,
                stdin=None,
                close_fds=False)
            if wait:
                pipe.wait()
            return {'error':'', 'out':'', 'code':0, 'command':cmd}

        pipe = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if wait:
            pipe.wait()
        out, error = pipe.communicate()
        result = {'error':error, 'out':out, 'code':pipe.returncode, 'command':cmd}
        return result

#___________________________________________________________________________________________________ executeForOutput
    @classmethod
    def executeForOutput(cls, cmd, critical =None, shell =True, raiseExceptions =True):
        if shell and not StringUtils.isStringType(cmd):
            cmd = ' '.join(cmd)

        try:
            out = subprocess.check_output(cmd, shell=shell)
        except Exception as err:
            if critical or (critical is None and raiseExceptions):
                raise err
            return None

        return out

#___________________________________________________________________________________________________ executeForStatus
    @classmethod
    def executeForStatus(cls, cmd, critical =None, shell =True, raiseExceptions =True):
        """ Returns true if the command executed successfully. """
        if shell and not StringUtils.isStringType(cmd):
            cmd = ' '.join(cmd)

        stat = subprocess.call(cmd, shell=shell)

        if stat:
            if critical or (critical is None and raiseExceptions):
                raise Exception('Command execution failed')
            else:
                return False

        return True

#___________________________________________________________________________________________________ download
    @classmethod
    def download(cls, url, target, httpsVerify =False, critical =None, raiseExceptions =True):
        try:
            import requests
            hasRequests = True
        except Exception:
            requests    = None
            hasRequests = False

        try:
            if url.startswith('ftp') or not hasRequests:
                res = urlopen(url)
            else:
                res = requests.get(url, verify=httpsVerify)
        except Exception as err:
            if critical or (critical is None and raiseExceptions):
                raise err
            else:
                print(err)
                return False

        failed = not res or (hasattr(res, 'status_code') and res.status_code != 200)
        if failed:
            if critical or (critical is None and raiseExceptions):
                raise Exception('Download failed')
            else:
                return False

        f = open(target, 'w')
        f.write(res.content if hasattr(res, 'content') else res.read())
        f.close()

        return True

#___________________________________________________________________________________________________ copy
    @classmethod
    def copy(cls, source, destination, echo =False):
        if os.path.isdir(source):
            try:
                shutil.copytree(source, destination)
            except Exception:
                try:
                    shutil.copy2(source, destination)
                except Exception:
                    print('FAILED TO COPY:\n    FROM: %s\n      TO: %s' % (source, destination))
                    return False
        else:
            try:
                shutil.copy2(source, destination)
            except Exception:
                try:
                    shutil.copytree(source, destination)
                except Exception:
                    print('FAILED TO COPY:\n    FROM: %s\n      TO: %s' % (source, destination))
                    return False

        if echo:
            print('COPIED:\n    FROM: %s\n      TO: %s' % (source, destination))
        return True

#___________________________________________________________________________________________________ gzip
    @classmethod
    def gzip(cls, target):
        cmd = ['gzip', target]
        if cls.executeForStatus(cmd):
            return target + '.gz'

        return None

#___________________________________________________________________________________________________ ungzip
    @classmethod
    def ungzip(cls, target):
        cmd = ['gunzip', target]
        if cls.executeForStatus(cmd):
            return target[:-3]

        return target

#___________________________________________________________________________________________________ tar
    @classmethod
    def tar(cls, zipTarget, fileList, append =False, newerOnly =False, gzip =True):
        if not isinstance(fileList, list):
            fileList = [fileList]

        if not zipTarget:
            zipTarget = 'myTarFile_' + datetime.datetime.utcnow().strftime('%Y%b%d-%H%M')

        if not zipTarget.endswith('.tar.gz'):
            zipTarget += '.tar.gz'

        originalDirectory = os.curdir
        rootPath          = os.path.dirname(zipTarget)
        if rootPath:
            cls.changeDir(rootPath)
            zipTarget = os.path.basename(zipTarget)

            cleanFiles = []
            for f in fileList:
                if f.startswith(rootPath):
                    f = f[len(rootPath):]
                    if f.startswith(os.sep):
                        f = f[1:]
                cleanFiles.append(f)
            fileList = cleanFiles

        flags = ''
        if append:
            flags += 'A'
        else:
            flags += 'c'
            if os.path.exists(zipTarget):
                cls.remove(zipTarget)

        if newerOnly:
            flags += 'u'

        if gzip:
            flags += 'z'

        try:
            cmd = 'tar -%spvf %s %s' % (flags, zipTarget, ' '.join(fileList))
            cls.executeForStatus(cmd)
        except Exception:
            cls.changeDir(originalDirectory)
            return None

        cls.changeDir(originalDirectory)

        if rootPath:
            return os.path.join(rootPath, zipTarget)
        return zipTarget

#___________________________________________________________________________________________________ untar
    @classmethod
    def untar(cls, zipSource, overwriteAll =True, gzip =None):
        flags = ''
        if gzip or (gzip is None and zipSource.endswith('.gz')):
            flags += 'z'

        doubleFlags = []
        if overwriteAll:
            doubleFlags.append('--overwrite')

        originalDirectory = os.curdir
        d = os.path.dirname(zipSource)
        if d:
            cls.changeDir(d)

        try:
            cmd = 'tar -%sxpvf %s %s' % (flags, ' '.join(doubleFlags), zipSource)
            cls.executeForStatus(cmd)
        except Exception:
            cls.changeDir(originalDirectory)
            return False

        cls.changeDir(originalDirectory)
        return True

#___________________________________________________________________________________________________ do7zip
    @classmethod
    def do7zip(cls, zipTarget, fileList, append =False):
        """Don't use 7zip except for isolated files. It's not recursive."""

        if not isinstance(fileList, list):
            fileList = [fileList]

        try:
            if not append:
                if os.path.exists(zipTarget):
                    cls.remove(zipTarget)

            cmd = '7za a %s %s' % (zipTarget, ' '.join(fileList))
            cls.executeForStatus(cmd)
        except Exception as err:
            print(err)
            return False

        return True

#___________________________________________________________________________________________________ un7zip
    @classmethod
    def un7zip(cls, zipSource, targetPath =None, overwriteAll =True):
        try:
            flags = []
            if targetPath:
                flags.append('-o' + targetPath)

            if overwriteAll:
                flags.append('-y')

            cmd = '7za e %s %s' % (' '.join(flags), zipSource)
            cls.executeForStatus(cmd)
        except Exception as err:
            print(err)
            return False

        return True

#___________________________________________________________________________________________________ move
    @classmethod
    def move(cls, source, destination):
        try:
            shutil.move(source, destination)
        except Exception:
            return False

        return True

#___________________________________________________________________________________________________ remove
    @classmethod
    def remove(cls, path, throwError =False):
        if not os.path.exists(path):
            return True

        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except Exception as err1:
                try:
                    os.rmdir(path)
                except Exception as err2:
                    if throwError:
                        print('ERROR:', err1)
                        raise err2
                    return False
        elif os.path.islink(path):
            try:
                os.unlink(path)
            except Exception as err:
                if throwError:
                    raise err
                return False
        else:
            try:
                os.remove(path)
            except OSError as err1:
                try:
                    os.rmdir(path)
                except Exception as err2:
                    if throwError:
                        print('ERROR:', err1)
                        raise err2
                    return False

        return True

#___________________________________________________________________________________________________ findMatchingDir
    @classmethod
    def findMatchingDir(cls, pattern, path =None):
        if not path:
            path = os.getcwd()

        for item in os.listdir(path):
            if not os.path.isdir(item):
                continue

            res = re.compile(pattern).search(item)
            if res:
                return item

        return None

#___________________________________________________________________________________________________ changePermissions
    @classmethod
    def changePermissions(
            cls, permissions ='777', path =None, owner =None, group =None, recursive =True
    ):
        flags = []
        if recursive:
            flags.append('-r')
        flags = ' '.join(flags)

        try:
            if not cls.executeForStatus('chmod %s %s %s' % (flags, str(permissions), path)):
                return False
        except Exception:
            return False

        if owner and group:
            cls.executeForStatus('chown %s %s:%s %s' % (flags, owner, group, path))
        elif owner:
            cls.executeForStatus('chown %s %s %s' % (flags, owner, path))
        elif group:
            cls.executeForStatus('chgrp %s %s %s' % (flags, group, path))

        return True

#___________________________________________________________________________________________________ _changeDir
    @classmethod
    def changeDir(cls, path):
        os.chdir(path)

#___________________________________________________________________________________________________ listDir
    @classmethod
    def listDir(cls, path =None, dirs =True, files =True, absolute =True):
        out = []
        if not path:
            path = os.curdir

        src = os.listdir(path)
        for s in src:
            target = os.path.join(path, s)
            if dirs and os.path.isdir(target):
                out.append(target if absolute else s)

            if files and os.path.isfile(target):
                out.append(target if absolute else s)

        return out
