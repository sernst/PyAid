# CoffeescriptDependency.py
# (C)2011-2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import re
import inspect

#___________________________________________________________________________________________________ CoffeescriptDependency
from pyaid.string.StringUtils import StringUtils


class CoffeescriptDependency(object):

#===================================================================================================
#                                                                                       C L A S S

    REGISTRY            = 'SFLOW.r'

    INCLUDE_TYPE        = 'include'
    IMPORT_TYPE         = 'import'
    REQUIRE_TYPE        = 'require'
    MODULE_TYPE         = 'module'
    LIB_TYPE            = 'lib'
    SDK_FILES           = 'sdk'
    API_FILES           = 'api'
    EXEC_TYPE           = 'exec'
    TARGET_TYPE         = 'target'

    EXTENSION           = 'coffee'
    COMPILED_EXTENSION  = 'js'
    ASSEMBLED_EXTENSION = 'ccs'
    CACHE_EXTENSION     = 'ics'
    EXEC_FILES          = 'exec'
    LIB_FILES           = 'lib'
    CONTROL_CHAR        = '-'

    IMPORT_PATTERN    = re.compile('^[\s\t]*#[\s\t]*imports?[\s\t]*(.+)')
    REQUIRE_PATTERN   = re.compile('^[\s\t]*#[\s\t]*requires?[\s\t]*(.+)')
    TARGET_PATTERN    = re.compile('^[\s\t]*#[\s\t]*targets?[\s\t]*(.+)')
    INCLUDE_PATTERN   = re.compile('^[\s\t]*#[\s\t]*includes?[\s\t]*(.+)')
    MODULE_PATTERN    = re.compile('^[\s\t]*#[\s\t]*modules?[\s\t]*(.+)')

    FLAGS_PATTERN     = re.compile('(^|\n)[\s\t]*#[\s\t]*flags?[\s\t]*(?P<flags>.+)')

    SEARCH_EXPRESSION = '(?<![A-Za-z0-9_\.\'"])##NAME##(?![A-Za-z0-9_])'

#___________________________________________________________________________________________________ __init__
    def __init__(self, packageOrPath =None, rootPath =None, dependencyType =None):
        self._cls = self.__class__

        self._rootPath = rootPath

        if packageOrPath.find(os.path.sep) != -1:
            self._package = self.packageFromPath(packageOrPath, self._rootPath)
        else:
            self._package = packageOrPath

        if dependencyType is None:
            if self.isExec:
                self._type = self._cls.EXEC_TYPE
            elif self.isLib:
                self._type = self._cls.LIB_TYPE
            else:
                self._type = self._cls.IMPORT_TYPE
        else:
            self._type = dependencyType

        self._searchPattern     = None
        self._replaceExpression = None
        self._flags             = []
        self._source            = None
        self._cacheSource       = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: source
    @property
    def source(self):
        return self._source

#___________________________________________________________________________________________________ GS: cacheSource
    @property
    def cacheSource(self):
        if not self._cacheSource:
            f = open(self.cachePath, 'r')
            self._cacheSource = f.read()
            f.close()

        return self._cacheSource

#___________________________________________________________________________________________________ GS: flags
    @property
    def flags(self):
        return self._flags

#___________________________________________________________________________________________________ GS: allowCaching
    @property
    def allowCaching(self):
        return 'nocache' not in self._flags

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return self._package.split('.')[-1]

#___________________________________________________________________________________________________ GS: searchPattern
    @property
    def searchPattern(self):
        if not self._searchPattern:
            self._searchPattern = re.compile(
                self._cls.SEARCH_EXPRESSION.replace('##NAME##', self.name))

        return self._searchPattern

#___________________________________________________________________________________________________ GS: registryName
    @property
    def registryName(self):
        return self._cls.REGISTRY + '.' + self.name

#___________________________________________________________________________________________________ GS: exists
    @property
    def exists(self):
        return os.path.exists(self.path)

#___________________________________________________________________________________________________ GS: path
    @property
    def path(self):
        return self._cls.pathFromPackage(self._package, self._rootPath) + '.' + self._getExtension()

#___________________________________________________________________________________________________ GS: cachePath
    @property
    def cachePath(self):
        return self._cls.pathFromPackage(self._package, self._rootPath) + '.' + self._cls.CACHE_EXTENSION

#___________________________________________________________________________________________________ GS: useCache
    @property
    def useCache(self):
        if not os.path.exists(self.cachePath):
            return False

        if not self.allowCaching:
            return False

        cachModified = os.path.getmtime(self.cachePath)
        lastModified = os.path.getmtime(self.path)
        return cachModified > lastModified

#___________________________________________________________________________________________________ GS: assembledPath
    @property
    def assembledPath(self):
        return self._cls.pathFromPackage(self._package, self._rootPath) + '.' + self._cls.ASSEMBLED_EXTENSION

#___________________________________________________________________________________________________ GS: compiledPath
    @property
    def compiledPath(self):
        return self._cls.pathFromPackage(self._package, self._rootPath) + '.' + self._cls.COMPILED_EXTENSION

#___________________________________________________________________________________________________ GS: package
    @property
    def package(self):
        return self._package

#___________________________________________________________________________________________________ GS: packagePath
    @property
    def packagePath(self):
        if os.path.exists(self.path):
            return os.path.dirname(self.path) + os.path.sep
        else:
            return self.path.replace('.' + self._getExtension(), '') + os.path.sep

#___________________________________________________________________________________________________ GS: rootPath
    @property
    def rootPath(self):
        return self._rootPath

#___________________________________________________________________________________________________ GS: isImport
    @property
    def isImport(self):
        return self._type == self._cls.IMPORT_TYPE

#___________________________________________________________________________________________________ GS: isInclude
    @property
    def isInclude(self):
        """Specifies that the dependency is a javascript include, to be prepended to the file but
        not compiled because it is already JS."""

        return self._type == self._cls.INCLUDE_TYPE

#___________________________________________________________________________________________________ GS: isRequire
    @property
    def isRequire(self):
        return self._type == self._cls.REQUIRE_TYPE

#___________________________________________________________________________________________________ GS: isModule
    @property
    def isModule(self):
        return self._type == self._cls.MODULE_TYPE

#___________________________________________________________________________________________________ GS: dependencyType
    @property
    def dependencyType(self):
        return self._type

#___________________________________________________________________________________________________ GS: isExec
    @property
    def isExec(self):
        p   = self._package
        cls = self._cls
        return p.endswith('.' + cls.EXEC_FILES) or p.endswith(cls.CONTROL_CHAR + cls.EXEC_FILES)

#___________________________________________________________________________________________________ GS: isLib
    @property
    def isLib(self):
        p   = self._package
        cls = self._cls
        return p.endswith('.' + cls.LIB_FILES) or p.endswith(cls.CONTROL_CHAR + cls.LIB_FILES)

#___________________________________________________________________________________________________ GS: isSDK
    @property
    def isSDK(self):
        p   = self._package
        cls = self._cls
        return p.endswith('.' + cls.SDK_FILES) or p.endswith(cls.CONTROL_CHAR + cls.SDK_FILES)

#___________________________________________________________________________________________________ GS: isAPI
    @property
    def isAPI(self):
        p   = self._package
        cls = self._cls
        return p.endswith('.' + cls.API_FILES) or p.endswith(cls.CONTROL_CHAR + cls.API_FILES)

#___________________________________________________________________________________________________ GS: isTarget
    @property
    def isTarget(self):
        return self.isExec or self.isLib

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ open
    def open(self):
        if self._source:
            return self._source

        f   = open(self.path, 'r')
        raw = f.read()
        f.close()

        res = self._cls.FLAGS_PATTERN.finditer(raw)
        if res:
            for r in res:
                for f in r.group('flags').strip().split(','):
                    f = f.strip().lower().replace(' ', '').replace('-', '').replace('_', '')
                    if f and not f in self._flags:
                        self._flags.append(f)

        #-------------------------------------------------------------------------------------------
        # REPLACE COMPILE VARIABLES
        reps = {} # NONE AT THE MOMENT
        for n,v in reps.items():
            raw = raw.replace(n, StringUtils.toUnicode(v))

        self._source = raw + '\n'
        return raw

#___________________________________________________________________________________________________ close
    def close(self):
        self._source      = None
        self._cacheSource = None

#___________________________________________________________________________________________________ isInList
    def isInList(self, targetsList):
        for t in targetsList:
            if self.compare(t):
                return True

        return False

#___________________________________________________________________________________________________ compareToPath
    def compareToPath(self, path):
        return self.path == path

#___________________________________________________________________________________________________ compareToPackage
    def compareToPackage(self, package):
        return self.package == package

#___________________________________________________________________________________________________ compare
    def compare(self, dependency):
        if isinstance(dependency, CoffeescriptDependency):
            return self.package == dependency.package
        elif dependency.find('/') != -1 or dependency.find('\\') != -1:
            return self.compareToPath(dependency)
        else:
            return self.compareToPackage(dependency)

#___________________________________________________________________________________________________ __string__
    def __string__(self):
        return '<CoffeescriptDependency: %s | %s>' % (self._type, self.package)

#___________________________________________________________________________________________________ trace
    def trace(self):
        for p in dir(self):
            try:
                if p[0] == '_' or p[0].lower() != p[0]:
                    continue

                if inspect.isfunction(getattr(self, p)):
                    continue

                if inspect.ismethod(getattr(self, p)):
                    continue

                print(p + ': ' + str(getattr(self, p, 'NOT AVAILABLE')))
            except Exception:
                print('FAILED TO ACCESS: ' + str(p))
                continue

#___________________________________________________________________________________________________ create
    @staticmethod
    def create(src, rootPath):
        res = CoffeescriptDependency.createImport(src, rootPath)
        if res:
            return res

        res = CoffeescriptDependency.createRequire(src, rootPath)
        if res:
            return res

        res = CoffeescriptDependency.createModule(src, rootPath)
        if res:
            return res

        res = CoffeescriptDependency.createTarget(src, rootPath)
        if res:
            return res

        res = CoffeescriptDependency.createInclude(src, rootPath)
        if res:
            return res

        return None

#___________________________________________________________________________________________________ createImport
    @classmethod
    def createImport(cls, src, rootPath):
        return cls._createFromPattern(src, cls.IMPORT_PATTERN, cls.IMPORT_TYPE, rootPath)

#___________________________________________________________________________________________________ createInclude
    @classmethod
    def createInclude(cls, src, rootPath):
        return cls._createFromPattern(src, cls.INCLUDE_PATTERN, cls.INCLUDE_TYPE, rootPath)

#___________________________________________________________________________________________________ createRequire
    @classmethod
    def createRequire(cls, src, rootPath):
        return cls._createFromPattern(src, cls.REQUIRE_PATTERN, cls.REQUIRE_TYPE, rootPath)

#___________________________________________________________________________________________________ createModule
    @classmethod
    def createModule(cls, src, rootPath):
        return cls._createFromPattern(src, cls.MODULE_PATTERN, cls.MODULE_TYPE, rootPath)

#___________________________________________________________________________________________________ createTarget
    @classmethod
    def createTarget(cls, src, rootPath):
        return cls._createFromPattern(src, cls.TARGET_PATTERN, cls.TARGET_TYPE, rootPath)

#___________________________________________________________________________________________________ packageFromPath
    @classmethod
    def packageFromPath(cls, path, rootPath, extension =None, compiledExtension =None):
        if extension is None:
            extension = cls.EXTENSION

        if compiledExtension is None:
            compiledExtension = cls.COMPILED_EXTENSION

        package = path.replace(rootPath, '')\
                      .replace('.' + extension, '')\
                      .replace('.' + compiledExtension, '')

        return package.replace(os.path.sep, '.')

#___________________________________________________________________________________________________ pathFromPackage
    @classmethod
    def pathFromPackage(cls, package, rootPath):
        return rootPath + package.replace('.', os.sep)

#___________________________________________________________________________________________________ localPathFromPackage
    @classmethod
    def localPathFromPackage(cls, package):
        return package.replace('.', os.sep)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getExtension
    def _getExtension(self, override =None):
        if override:
            return override
        elif self._type == CoffeescriptDependency.INCLUDE_TYPE:
            return CoffeescriptDependency.COMPILED_EXTENSION

        return CoffeescriptDependency.EXTENSION

#___________________________________________________________________________________________________ _createFromPattern
    @staticmethod
    def _createFromPattern(src, pattern, dependencyType, rootPath):
        res = pattern.search(src)
        if res and len(res.groups()) > 0 and len(res.groups()[0]) > 0:
            return CoffeescriptDependency(
                res.groups()[0].strip(),
                rootPath=rootPath,
                dependencyType=dependencyType)
        else:
            return None

