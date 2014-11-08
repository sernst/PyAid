# CoffeescriptBuilder.py
# (C)2011-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os
import re
import getopt
from pyaid.dict.DictUtils import DictUtils

from pyaid.interactive.queries import queryYesNoQuit
from pyaid.debug.Logger import Logger
from pyaid.system.SystemUtils import SystemUtils
from pyaid.web.coffeescript.CoffeescriptAnalyzer import CoffeescriptAnalyzer
from pyaid.web.coffeescript.CoffeescriptDependency import CoffeescriptDependency

# AS NEEDED: from pyaid.web.coffeescript.IncludeCompressor import IncludeCompressor

#___________________________________________________________________________________________________ CoffeescriptBuilder
class CoffeescriptBuilder(object):
    """A class for..."""

    CLASS_PATTERN         = '^[\s\t]*class[\s\t]+(?P<class>[^\s\t\r\n]+)[\s\t]*'
    MISSING_CLASS_PATTERN = '[\s\t\(\[\{\!]+(?=[A-Z])(?P<class>[A-Za-z0-9_]+)(?P<next>[^A-Za-z0-9_]+)'

    _WARN_ID_MISSING_IMPORT = 'MISSING-IMPORT'

    _GLOBAL_CLASSES = [
        'SFLOW', 'PAGE', 'FB', 'Math', 'JSON', 'String', 'ActiveXObject', 'Date', 'DOMParser',
        'RegExp', 'Object', 'Number', 'Array', 'Function', 'XMLHttpRequest']

    _results = None
    _missing = None

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(
            self, targetPackageOrPath, rootPath, verbose =True, debug =False, trace = False,
            force =False, compress =False, buildOnly =False
    ):
        """Creates a new instance of CoffeescriptBuilder."""

        self.buildOnly = buildOnly

        self._imports           = dict()
        self._requires          = dict()
        self._includes          = dict()
        self._report            = dict()
        self._warnings          = []
        self._dependencyReport  = dict()
        self._verbose  = verbose
        self._log      = Logger(self, printOut=True)
        self._trace    = trace
        self._debug    = debug
        self._targets  = []
        self._force    = force
        self._compress = compress
        self._rootPath = rootPath

        if not isinstance(targetPackageOrPath, CoffeescriptDependency):
            target = CoffeescriptDependency(targetPackageOrPath, rootPath, None)
        else:
            target = targetPackageOrPath

        if target.exists:
            self._targets.append(target)
        else:
            csFiles = CoffeescriptBuilder.getScriptsInPath(target.packagePath)

            # Look for exec matches first
            for f in csFiles:
                testTarget = CoffeescriptDependency(f, rootPath, None)
                if testTarget.isExec:
                    self._targets.append(testTarget)

            # Look for lib matches second. Lib matches are tested as a second pass because
            # constructing all exec files first potentially optimizes the import process for
            # the libraries.
            for f in csFiles:
                testTarget = CoffeescriptDependency(f, rootPath, None)
                if testTarget.isLib:
                    self._targets.append(testTarget)

        if len(self._targets) == 0:
            print('\n\n')
            self._log.write('No targets exist for: %s. Compilation aborted.' % targetPackageOrPath)
            print('\n')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: report
    @property
    def report(self):
        return self._report

#___________________________________________________________________________________________________ GS: warnings
    @property
    def warnings(self):
        return self._warnings

#___________________________________________________________________________________________________ GS: imports
    @property
    def imports(self):
        return self._imports

#___________________________________________________________________________________________________ GS: requires
    @property
    def requires(self):
        return self._requires

#___________________________________________________________________________________________________ GS: includes
    @property
    def includes(self):
        return self._includes

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ construct
    def construct(self):
        """Doc..."""
        for t in self._targets:
            self._report[t.package] = -1
            if t.isLib:
                self._constructLibrary(t)
            else:
                self._constructTarget(t)

            if self._compress:
                print('COMPRESSING:', t.package)
                from pyaid.web.coffeescript.IncludeCompressor import IncludeCompressor
                ic = IncludeCompressor()
                if not ic.compressFile(t.compiledPath):
                    print('COMPRESSION FAILURE:', t.compiledPath)

        return self._targets

#___________________________________________________________________________________________________ compileAllOnPath
    @staticmethod
    def compileAllOnPath(path, rootPath =None, recursive =False, debug =False, trace =False,
                         force =False, compress=False):

        CoffeescriptBuilder._results = ''
        CoffeescriptBuilder._missing = {}
        if recursive:
            print('RECURSIVE COMPILE AT: ' + path)
            def walker(paths, dirName, names):
                out = CoffeescriptBuilder._compileAllInDirectory(
                    os.path.join(paths[0], dirName), paths[1], debug=debug, trace=trace,
                    force=force, compress=compress
                )
                CoffeescriptBuilder._results += out['res']
                for n,v in DictUtils.iter(out['missing']):
                    if n in CoffeescriptBuilder._missing:
                        continue
                    CoffeescriptBuilder._missing[n] = v

            os.path.walk(path, walker, [path, rootPath])
            print('\n\nCOMPILATION RESULTS:' + CoffeescriptBuilder._results)

            if CoffeescriptBuilder._missing:
                print('\n\nMISSING IMPORTS:' + '\n\n')
                for n,v in DictUtils.iter(CoffeescriptBuilder._missing):
                    print(v['class'] + ' [LINE: #' + str(v['line']) + ' | ' + v['package'] + ']')
        else:
            print('COMPILING DIRECTORY: ' + path)
            CoffeescriptBuilder._compileAllInDirectory(
                path, rootPath, debug=debug, trace=trace, force=force, compress=compress)

#___________________________________________________________________________________________________ getScriptsInPath
    @staticmethod
    def getScriptsInPath(path):
        files = []

        for f in os.listdir(path):
            if f.lower().endswith('.' + CoffeescriptDependency.EXTENSION):
                files.append(os.path.join(path, f))

        return files

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _constructLibrary
    def _constructLibrary(self, target):
        try:
            if self._verbose:
                print("\n\n" + ('-'*100) + '\n')
                self._log.add(
                    'LIBRARY: %s\n\tsource: %s\n\troot: %s' % (
                        target.package, target.path, target.rootPath))

            #---------------------------------------------------------------------------------------
            # Compile all includes using library data
            targets, imports, modules, includes = self._getLibraryData(target)

            # Process requires for all of the targets
            for t in (targets + imports + modules):
                self._processRequires(t)

            #---------------------------------------------------------------------------------------
            # IMPORTS

            # Compile all excludes skipping any exec or lib files that are listed in the import
            # statements.
            importExcludes = []
            for t in targets:
                for imp in self._imports[t.package]:
                    if not (imp.isExec or imp.isLib or imp.isInList(importExcludes)):
                        importExcludes.append(imp)

            # Compile all imports needed for the library. Any excludes are added to the shared
            # library to be made accessible via the VIZME registry.
            libImports    = []
            sharedImports = []
            for t in (imports + modules):
                for imp in self.imports[t.package]:
                    if not imp.isInList(libImports):
                        if imp.isInList(importExcludes):
                            if not imp.isInList(sharedImports):
                                sharedImports.append(imp)
                        else:
                            libImports.append(imp)
            libImports.append(target)

            #---------------------------------------------------------------------------------------
            # INCLUDES

            # Compile all includes to exclude from the library because they already exist in a
            # target.
            includeExcludes = []
            for t in targets:
                for inc in self._includes[t.package]:
                    if not inc.isInList(includeExcludes):
                        includeExcludes.append(inc)

            # Compile all includes needed for the library.
            libIncludes    = []
            sharedIncludes = []

            # Add the top-level includes directly because they are not handled implicitly like
            # the import case
            for inc in includes:
                if inc.isInList(includeExcludes):
                    sharedIncludes.append(inc)
                else:
                    libIncludes.append(inc)

            for t in (imports + modules):
                for inc in self.includes[t.package]:
                    if not inc.isInList(libIncludes):
                        if inc.isInList(includeExcludes):
                            if not inc.isInList(sharedIncludes):
                                sharedIncludes.append(inc)
                        else:
                            libIncludes.append(inc)

            if self._verbose:
                print('\n')
                s = 'IMPORTING:'
                for imp in libImports:
                    s += '\n\t' + imp.package
                for inc in libIncludes:
                    s += '\n\tEXTERNAL: ' + inc.package
                self._log.add(s)

                print('\n')
                s = 'EXCLUDING:'
                for imp in sharedImports:
                    s += '\n\t' + imp.package
                for inc in sharedIncludes:
                    s += '\n\tEXTERNAL: ' + inc.package
                self._log.add(s)

            #---------------------------------------------------------------------------------------
            # Construct intermediate compilation file.
            assembledFile = self._assembleFile(
                target, libImports, sharedImports, {'modules':modules}
            )
            if assembledFile is None:
                self._log.write('ERROR: File assembly failed.')
                return

            #---------------------------------------------------------------------------------------
            # Compile to Javascript
            if not self.buildOnly:
                self._compileToJavascript(target, assembledFile, libIncludes)

            if self._verbose:
                print("\n" + ('-'*100) + '\n')

        except Exception as err:
            print("\n\n\n")
            self._log.writeError(
                'ERROR: Compilation failure for: %s\n\tsource: %s\n\troot: %s'
                % (target.package, target.path, target.rootPath), err)

#___________________________________________________________________________________________________ _constructTarget
    def _constructTarget(self, target):
        try:
            if self._verbose:
                print("\n\n" + ('-'*100) + '\n')
                self._log.write(
                    'EXECUTABLE: %s\n\tsource: %s\n\troot: %s'
                    % (target.package, target.path, target.rootPath) )

            #---------------------------------------------------------------------------------------
            # Handle imports and requires
            self._parseIncludes(target)
            self._processRequires(target)

            if self._verbose:
                s = 'IMPORTING:'
                for imp in self._imports[target.package]:
                    s += '\n\t' + imp.package
                self._log.write(s)

            #---------------------------------------------------------------------------------------
            # Construct intermediate compilation file.
            assembledFile = self._assembleFile(target)
            if assembledFile is None:
                self._log.write('ERROR: File assembly failed.')
                return

            #---------------------------------------------------------------------------------------
            # Compile to Javascript
            if not self.buildOnly:
                self._compileToJavascript(target, assembledFile)

            if self._verbose:
                print("\n" + ('-'*100) + '\n')

        except Exception as err:
            print("\n\n\n")
            self._log.writeError(
                'ERROR: Compilation failure for: %s\n\tsource: %s\n\troot: %s' % (
                    target.package, target.path, target.rootPath), err)

#___________________________________________________________________________________________________ _createOutputFile
    def _createOutputFile(self, target):
        """Creates the output ccs assembly file for writing."""
        outFile = target.assembledPath
        try:
            return open(outFile, 'w')
        except Exception as err:
            print("\n\n")
            self._log.write('Unable To Open output file: ' + str(outFile) + '\n' \
                            'Check to make sure you have write permissions to that directory.')
            return None

#___________________________________________________________________________________________________ _writeRegistryEntry
    def _writeRegistryEntry(self, out, cacheOut, entry):
        # If there is an unconsumed registryEntry write it.
        if not entry:
            return None

        s = '\n' + entry + '\n'
        out.write(s)

        if cacheOut:
            cacheOut.write(s)
        return None

#___________________________________________________________________________________________________ _assembleFile
    def _assembleFile(self, target, importOverride =None, replacements =None, assembleData =None):

        #-------------------------------------------------------------------------------------------
        # CREATE FILE
        # Creates the file to write
        out = self._createOutputFile(target)
        if not out:
            self._log('ERROR: Unable to create output file')
            return

        #-------------------------------------------------------------------------------------------
        # DEFINE IMPORTS
        # Specify the files to import. For exec files the default packages are included, for
        # libraries these are overridden based on library target dependencies.
        targetImports = self._imports[target.package] if importOverride is None else importOverride

        replacements   = replacements if isinstance(replacements, list) else []
        classList      = []

        #-------------------------------------------------------------------------------------------
        # Note the last dependency so that the glue script can be appended prior
        lastDep = targetImports[-1]

        #-------------------------------------------------------------------------------------------
        # DEPENDENCY ASSEMBLY LOOP
        print('\n')
        for dep in targetImports:
            dep.open()

            if self._force or not dep.useCache:
                if not self._compileDependency(dep, out, replacements, targetImports, classList):
                    return None
                continue

            self._log.write('\tFROM CACHE: ' + dep.package)
            out.write(dep.cacheSource)
            dep.close()

        out.close()

        if self._verbose:
            print('\n')
            self._log.add('CONSTRUCTED: ' + out.name)

        return out.name

#___________________________________________________________________________________________________ _compileDependency
    def _compileDependency(self, dep, out, replacements, targetImports, classList):
        classPattern   = re.compile(CoffeescriptBuilder.CLASS_PATTERN)
        missingPattern = re.compile(CoffeescriptBuilder.MISSING_CLASS_PATTERN)

        #-------------------------------------------------------------------------------------------
        # MISSING DEPENDENCIES
        # Handle missing dependencies
        if not os.path.exists(dep.path):
            print("\n\n")
            self._log.write('ERROR: ' + dep.package + ' package does not exist at: ' + dep.path)
            return False

        lastWhitespace   = ''
        openParens       = 0
        openBrackets     = 0
        openBraces       = 0
        skipNextLine     = False
        methodName       = ''
        className        = ''
        registryEntry    = None

        raw = dep.source
        dep.close()

        s = '\n\n\t#' + ('%'*100) + '\n\t#' + ('%'*100) + '\n#\t\t' + dep.package + '\n'

        out.write(s)
        if dep.allowCaching:
            cacheOut = open(dep.cachePath, 'w')
            cacheOut.write(s)
        else:
            try:
                if os.path.exists(dep.cachePath):
                    os.remove(dep.cachePath)
            except Exception as err:
                pass

            cacheOut = None

        self._log.write('\tCOMPILING: ' + dep.package)

        analyzer = CoffeescriptAnalyzer(raw, debug=self._debug)
        analyzer.analyze()

        #---------------------------------------------------------------------------------------
        # COMPILE
        # Line by line compile to ccs output file
        for l in analyzer:

            #-----------------------------------------------------------------------------------
            # RETARGET CLASS ACCESSORS TO VIZME registry
            # All classes (except internal class references) are made to
            # VIZME registry ClassName to prevent class conflicts.
            for rep in replacements + targetImports:
                if rep != dep:
                    offset = 0
                    res    = rep.searchPattern.finditer(l.redacted)
                    for r in res:
                        start = r.start() + offset
                        end   = r.end() + offset

                        if self._trace:
                            self._log.write(
                                'RETARGET: ' + l.source[start:end] + ' | ' + str(r.groupdict())
                            )

                        # Make the replacement and adjust offsets for additional replacements
                        l.insert(start, end, rep.registryName)
                        offset += len(rep.registryName) - end + start

            #-----------------------------------------------------------------------------------
            # IDENTIFY CLASS DEFINITIONS
            # Find class definitions so they can be added to the VIZME registry.
            res = classPattern.search(l.redacted)
            if res:
                registryEntry = self._writeRegistryEntry(out, cacheOut, registryEntry)
                className     = res.group('class').strip()
                registryEntry = '\n%s.%s ?= %s' % (CoffeescriptDependency.REGISTRY, className, className)
                classList.append(className)

            #-----------------------------------------------------------------------------------
            # CHECK FOR MISSING CLASSES
            # Search and find any missing class imports. If a possible missing import is found
            # flag it in the response.
            res = missingPattern.finditer(l.redacted)
            if res:
                for r in res:
                    cn    = r.group('class').strip()
                    start = r.start()

                    if cn == className:
                        continue

                    # Ignore anything in all CAPS!
                    if cn.upper() == cn:
                        continue

                    # Ignore globally defined objects and classes
                    if cn in CoffeescriptBuilder._GLOBAL_CLASSES + analyzer.globalObjects:
                        continue

                    self._warnings.append({
                        'id':CoffeescriptBuilder._WARN_ID_MISSING_IMPORT,
                        'class':cn,
                        'line':l.lineNumber,
                        'package':dep.package })

                    print('\n')
                    self._log.write(
                        'WARNING: Possible missing import\n\tmissing: %s\n\tfrom: %s [line #%s]'
                        % (cn, dep.package, str(l.lineNumber)) )

            #-----------------------------------------------------------------------------------
            # LINE DEBUGGER ANALYSIS
            c                = l.redacted.strip()
            skip             = skipNextLine or not l.isSignificant
            skipNextLine     = False

            if not skip:
                skips = ['class', 'try', 'catch', 'else', 'when', '.', '+', '-', '/', '=',
                         '*', ',', 'and', 'or']
                for s in skips:
                    if c.startswith(s):
                        skip = True
                        break

            if not skip:
                skips         = ['->', '=>']
                methodPattern = re.compile('^(?P<method>[^:]+)')

                for s in skips:
                    if c.endswith(s):
                        skip = True
                        res  = methodPattern.search(c)
                        if res and res.group('method'):
                            methodName = res.group('method')
                        elif c.startswith('$'):
                            methodName = '$'

                        break

            # Check for line continuations
            if l.isSignificant:
                skips = ['.', '+', '-', '/', '=', '*', ',', 'and', 'or']
                for s in skips:
                    if c.endswith(s):
                        skipNextLine = True
                        break

            if self._trace:
                self._log.write(c.replace('\n', '')
                                + ('\n\t@@@@ skip: ' + str(skip)
                                   + '\n\t@@@@ parens: ' + str(openParens)
                                   + '\n\t@@@@ braces: ' + str(openBraces)
                                   + '\n\t@@@@ brackets: ' + str(openBraces)
                                   + '\n\t@@@@ skipNext: ' + str(skipNextLine)))

            if self._debug and not skip and openParens == 0 and openBraces == 0 and openBrackets == 0:
                debugLine = 'window.___vmiDebug(\'%s\', \'%s\', \'%s\', %s)\n' % \
                            (dep.package, className, methodName, str(l.lineNumber))

                indent = len(l.indent) > len(lastWhitespace)
                dedent = len(l.indent) < len(lastWhitespace)

                skips = [')', ']', '}']
                skip  = False
                for s in skips:
                    if c.startswith(s):
                        skip = True
                        break

                if dedent and skip:
                    lastWhitespace = lastWhitespace
                else:
                    lastWhitespace = l.indent

                codePattern = re.compile('(?P<code>[^\s\t\n]+)')
                res = codePattern.search(c)
                if not res or len(res.groupdict()['code']) == 0:
                    if self._trace:
                        self._log.write('EMPTY: "' + c + '"')
                    debugLine = ''

                l.insert(0, 0, l.indent + debugLine)

            if l.isSignificant:
                openParens   += l.redacted.count('(') - l.redacted.count(')')
                openBrackets += l.redacted.count('[') - l.redacted.count(']')
                openBraces   += l.redacted.count('{') - l.redacted.count('}')

            #---------------------------------------------------------------------------------------
            # WRITE MODIFIED OUTPUT
            out.write(l.source)

            if cacheOut:
                cacheOut.write(l.source)

        self._writeRegistryEntry(out, cacheOut, registryEntry)

        if cacheOut:
            cacheOut.close()

        return True

#___________________________________________________________________________________________________ _compileToJavascript
    def _compileToJavascript(self, target, assembledFile, jsIncludeOverrides =None):

        # Use the Coffeescript compiler to create a JS compilation of the assembled CS file
        result = SystemUtils.executeCommand(['coffee', '-c', '--bare', assembledFile])
        status = result['code']
        output = result['out']
        errors         = 0
        forceVerbose   = False

        #-------------------------------------------------------------------------------------------
        # ERROR HANDLING
        #    Check the error status of the compilation process and if a failure occurred parse the
        #    error results for display and logging.
        if status:
            outputLines = str(output).replace('\r','').split('\n')
            for line in outputLines:
                if line.startswith('Error:') or line.startswith('SyntaxError:'):
                    errors += 1
                    result = CoffeescriptBuilder._parseError(line)
                    if result:
                        self._log.add(result)
                    else:
                        forceVerbose = True

        if forceVerbose:
            self._log.add(output)

        self._report[target.package] = errors
        if self._verbose:
            print("\n\n")
            if errors == 0 and status == 0:
                self._log.write('Compilation complete: ' + target.compiledPath)
            else:
                self._log.write('Compilation FAILED: ' + target.package)

        f   = open(target.compiledPath, 'r')
        res = f.read()
        f.close()

#___________________________________________________________________________________________________ _parseIncludes
    def _parseIncludes(self, target, rootTarget =None):
        """Doc..."""
        if rootTarget is None:
            rootTarget = target

        if not rootTarget.package in self._imports:
            self._imports[rootTarget.package] = []

        if not rootTarget.package in self._requires:
            self._requires[rootTarget.package] = []

        if not rootTarget.package in self._includes:
            self._includes[rootTarget.package] = []

        if not os.path.exists(target.path):
            print("\n")
            self._log.add('WARNING: Missing import.\n\tPACKAGE: ' + target.package + '\n\tFILE: ' \
                          + target.path)
            print("\n")
            return

        f = open(target.path)
        for line in f:

            # import parse
            dependency = CoffeescriptDependency.createImport(line, self._rootPath)
            if dependency and not dependency.isInList(self._imports[rootTarget.package]):
                self._parseIncludes(dependency, rootTarget)
                self._imports[rootTarget.package].append(dependency)
                continue

            # require parse
            dependency = CoffeescriptDependency.createRequire(line, self._rootPath)
            if dependency and not dependency.isInList(self._imports[rootTarget.package]):
                self._requires[rootTarget.package].append(dependency)
                continue

            # include parse
            dependency = CoffeescriptDependency.createInclude(line, self._rootPath)
            if dependency and not dependency.isInList(self._includes[rootTarget.package]):
                self._includes[rootTarget.package].append(dependency)
                continue

        f.close()
        self._imports[rootTarget.package].append(target)

#___________________________________________________________________________________________________ _processRequires
    def _processRequires(self, target):
        currentTarget = self._imports[target.package].pop()
        while len(self._requires[target.package]) > 0:
            self._parseIncludes(self._requires[target.package].pop(0), target)

        outlist = []
        for item in self._imports[target.package]:
            if not item.isInList(outlist) and not item.compare(currentTarget):
                outlist.append(item)
        self._imports[target.package] = outlist
        self._imports[target.package].append(currentTarget)

#___________________________________________________________________________________________________ _getLibraryData
    def _getLibraryData(self, target):
        targets  = []
        modules  = []
        imports  = []
        includes = []

        src = open(target.path, 'r')
        for line in src:

            # target parse
            d = CoffeescriptDependency.create(line, self._rootPath)
            if not d:
                continue

            if d.dependencyType == CoffeescriptDependency.TARGET_TYPE:
                targets.append(d)
            elif d.dependencyType == CoffeescriptDependency.IMPORT_TYPE:
                imports.append(d)
            elif d.dependencyType == CoffeescriptDependency.REQUIRE_TYPE:
                imports.append(d)
            elif d.dependencyType == CoffeescriptDependency.INCLUDE_TYPE:
                includes.append(d)
            elif d.dependencyType == CoffeescriptDependency.MODULE_TYPE:
                modules.append(d)
            else:
                continue

            self._parseIncludes(d)

        src.close()

        return targets, imports, modules, includes

#___________________________________________________________________________________________________ _compileAllInDirectory
    @staticmethod
    def _compileAllInDirectory(path, rootPath =None, debug =False, trace =False, force =False,
                               compress=False):
        results = ''
        missing = {}
        count   = 0
        for f in CoffeescriptBuilder.getScriptsInPath(path):
            target = CoffeescriptDependency(f, rootPath)
            if not (target.exists and (target.isExec or target.isLib)):
                continue

            c = CoffeescriptBuilder(
                target, rootPath, debug=debug, trace=trace, force=force, compress=compress
            )
            c.construct()
            count += 1
            for n,v in DictUtils.iter(c.report):
                num = max(0, 60 - len(n))
                results += '\n' + n + ':' + ('.'*num)
                if v == 0:
                    results += 'SUCCESS'
                elif v > 0:
                    results += 'COMPILATION FAILED'
                else:
                    results += 'ASSEMBLY FAILED'

            if len(c.warnings) > 0:
                results += '[' + str(len(c.warnings)) + ' WARNINGS]'
                for v in c.warnings:
                    if not v['id'] == CoffeescriptBuilder._WARN_ID_MISSING_IMPORT:
                        continue

                    key = v['package'] + '-' + v['class'] + '-' + str(v['line'])
                    if key in missing:
                        continue

                    missing[key] = v

        if len(results) > 0:
            print('\nDIRECTORY ' + path + ' COMPILE RESULTS [' + str(count) + ']:' + results)
        return {'res':results, 'missing':missing}

#___________________________________________________________________________________________________ _parseError
    @staticmethod
    def _parseError(error):
        """ Parses errors of the format:
        "Error: In /vizme2/website/js/vmi/blog/author/exec.ccs, Parse error on line 181: Unexpected 'INDENT'"
        """

        ccsFile = None

        prefixReplacements = ['SyntaxError: In ', 'Error: In ']
        for p in prefixReplacements:
            error = error.replace(p,'')

        out = '\n-----------------------------------------------\nERROR: '
        try:
            sep     = error.index(',')
            ccsFile = error[:sep]
        except Exception:
            pass

        try:
            sep2    = error.index(':')
            out    += error[sep2+1:].strip() + '\n'
        except Exception:
            if error and sep:
                out += error[sep+1:].strip() + '\n'

        pattern = re.compile('line[\s\t]+(?P<linenumber>[0-9]+)')
        res     = pattern.search(error)
        if res and len(res.groups()) > 0:
            lineNumber = int(res.groups()[0]) - 1
        else:
            out += '    Unspecified location'
            return

        if ccsFile:
            padSize      = len(str(lineNumber + 3))
            jQueryName   = 'Exec Function (JQUERY Document ready)'
            functionName = None
            className    = None
            trace        = ''
            f       = open(ccsFile, 'r')
            for i, line in enumerate(f):
                if i > lineNumber + 4:
                    break

                if i <= lineNumber:
                    pattern = re.compile('^class[\s\t]+(?P<classname>[a-zA-Z0-9_]+)')
                    res     = pattern.search(line)
                    if res and len(res.groups()) > 0:
                        className = res.groups()[0]
                        functionName = None

                    pattern = re.compile('^\$[\s\t]*[-=]+>')
                    res     = pattern.search(line)
                    if res:
                        className = jQueryName
                        functionName = None

                    pattern = re.compile('[\s\t]*(?P<name>[a-zA-Z0-9_]+)[\s\t]*:[^-=>]*[-=]+>')
                    res     = pattern.search(line)
                    if res and len(res.groups()) > 0:
                        functionName = res.groups()[0]

                if i > lineNumber - 4:
                    marker = ">>" if i == lineNumber else "  "
                    trace += marker + str(i).rjust(padSize) + '| ' + line

            f.close()

            if functionName:
                out += "  " + ("METHOD" if className else "FUNCTION") + ": " + functionName + "\n"

            if className:
                out += "  " + ("CLASS" if className != jQueryName else "EXEC") + ": " + className + "\n"

            out += "  TRACE:\n" + trace

        return out + "\n"

###################################################################################################
###################################################################################################

#___________________________________________________________________________________________________ usage
def usage():
    print("""
        Builds a coffee script file of all dependencies and then compiles it to Javascript for
        deployment

        -t | --target    - Import to compile.
        -p | --path      - Path in which to compile all matching exec files.
        -r | --root      - Root path
        -a | --all       - Recursively compiles all exec files in path and its subpaths.
        -f | --full      - Full compile of everything located on the default path.
        -d | --debug     - Compiles in debug mode with explicit stack tracing.
        -c | --compress  - Compresses each file after it is compiled.
        -v | --verbose   - Verbose mode is used for debugging.
        --force          - Force compilation even if cache entries are valid.
    """)

#___________________________________________________________________________________________________ main
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hap:t:r:fdvc", [
            "help", "all", "path=","target=", "root=", "full", "debug", "verbose", "force",
            "compress" ])
    except getopt.GetoptError as err:
        print(str(err) + "\n")
        usage()
        sys.exit(2)

    target    = None
    path      = None
    root      = None
    recursive = False
    compress  = False
    full      = False
    debug     = False
    trace     = False
    force     = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("--force"):
            force = True
        elif o in ("-a", "--all"):
            recursive = True
        elif o in ("-p", "--path"):
            if a:
                path = a
        elif o in ("-t", "--target"):
            if a:
                target = a
        elif o in ("-r", "--root"):
            if a:
                root = a
        elif o in ("-f", "--full"):
            full = True
        elif o in ("-d", "--debug"):
            debug = True
        elif o in ("-v", "--verbose"):
            trace = True
        elif o in ("-c", "--compress"):
            compress = True
        else:
            print("\nUnknown argument: " + o + ". Unable to continue.\n\n")
            usage()
            sys.exit(2)

    if full:
        CoffeescriptBuilder.compileAllOnPath(
            path, root, True, debug, trace, force, compress=compress)
    elif target:
        if recursive:
            CoffeescriptBuilder.compileAllOnPath(
                path=CoffeescriptDependency.pathFromPackage(target, root),
                rootPath=root,
                recursive=True,
                debug=debug,
                trace=trace,
                force=force,
                compress=compress)
        else:
            CoffeescriptBuilder(
                target, root, debug=debug, trace=trace, force=force, compress=compress).construct()
    elif path:
        CoffeescriptBuilder.compileAllOnPath(
            path, root, recursive, debug, trace, force, compress=compress)
    else:
        print("\nNo path was specified. Would you like to compile the entire vmi domain?")
        result = queryYesNoQuit('Yes to continue:')

        if result != "yes":
            sys.exit()

        CoffeescriptBuilder.compileAllOnPath(path, root, True, debug, trace, force)

    print("\nOperation complete.\n")


###################################################################################################
###################################################################################################

if __name__ == '__main__':
    main()

