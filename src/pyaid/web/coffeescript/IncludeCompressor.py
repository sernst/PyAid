# IncludeCompressor.py
# (C)2010-2013
# Scott Ernst

from __future__ import print_function
from __future__ import absolute_import

import re
import sys
import os
import getopt

from pyaid.debug.Logger import Logger
from pyaid.interactive.queries import queryGeneralValue, queryFromList
from pyaid.system.SystemUtils import SystemUtils
import pyaid.units.SizeUnits as SizeUnits
# AS NEEDED: from pyaid.web.coffeescript.CoffeescriptBuilder import CoffeescriptBuilder

#___________________________________________________________________________________________________ IncludeCompressor
class IncludeCompressor(object):

#===================================================================================================
#                                                                                       C L A S S

    _REMOVE_COMMENT_RE      = re.compile('/\*.+\*/', re.DOTALL)
    _REMOVE_COMMENT_LINE_RE = re.compile('(^|\n)[\s\t]*//.+(\n|$)')

    JS_TYPE  = 'js'
    CSS_TYPE = 'css'

#___________________________________________________________________________________________________ __init__
    def __init__(self, compileCoffee =False):
        self._log           = Logger('IncludeCompressor')
        self._compileCoffee = compileCoffee

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ compress
    def compress(self, rootPath):
        if not self._fileExists(rootPath):
            return False
        elif os.path.isfile(rootPath):
            return self.compressFile(rootPath)
        else:
            return self.compressPath(rootPath)

#___________________________________________________________________________________________________ compressFile
    def compressFile(self, rootPath, directory =None):
        if not self._fileExists(rootPath):
            return False

        if self._compileCoffee:
            try:
                from pyaid.web.coffeescript.CoffeescriptBuilder import CoffeescriptBuilder
                CoffeescriptBuilder.compileAllOnPath(rootPath, os.path.dirname(rootPath), True)
                self._log.write('Coffeescript compiled.')
            except Exception as err:
                self._log.writeError('Failed to compile coffeescript file.', err)
                return False

        return self._compressFile(rootPath, directory)

#___________________________________________________________________________________________________ compressPath
    def compressPath(self, rootPath):
        # First compile any coffee scripts to js files
        if self._compileCoffee:
            try:
                from pyaid.web.coffeescript.CoffeescriptBuilder import CoffeescriptBuilder
                CoffeescriptBuilder.compileAllOnPath(rootPath, rootPath, True)
                self._log.write('Coffee scripts compiled.')
            except Exception as err:
                self._log.writeError('Failed to compile coffeescript files.', err)
                return False

        os.path.walk(rootPath, self._compressInFolder, None)
        self._log.write('Compression operation complete.')
        return True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _fileExists
    def _fileExists(self, rootPath):
        if not os.path.exists(rootPath):
            self._log.write('ERROR: [%s] does not exist. Operation aborted.' % rootPath)
            return False

        return True

#___________________________________________________________________________________________________ _compressFile
    def _compressFile(self, target, directory):
        # Skip compiled files.
        if target.endswith('comp.js') or target.endswith('comp.css'):
            return False

        if target.endswith('.js'):
            fileType = IncludeCompressor.JS_TYPE
        elif target.endswith('.css'):
            fileType = IncludeCompressor.CSS_TYPE
        else:
            return False

        if not directory:
            directory = ''
        if not directory.endswith(os.sep) and not target.startswith(os.sep):
            directory += os.sep

        inFile     = directory + target
        tempFile   = directory + target + '.temp'

        try:
            fh         = open(inFile, 'r')
            fileString = fh.read()
            fh.close()
        except Exception as err:
            self._log.writeError('FAILED: Unable to read ' + str(inFile), err)
            return False

        if fileType == IncludeCompressor.CSS_TYPE:
            fileString = fileString.replace('@charset "utf-8";', '')
            ofn        = (target[0:-3] + 'comp.css')
        else:
            ofn = (target[0:-2] + 'comp.js')

        try:
            fh = open(tempFile, 'w')
            fh.write(fileString)
            fh.close()
        except Exception as err:
            self._log.writeError('FAILED: Unable to write temp file ' + str(tempFile), err)
            return False

        outFile = directory + '/' + ofn

        cmd    = ['minify', '"%s"' % tempFile, '"%s"' % outFile]
        result = SystemUtils.executeCommand(cmd)
        if result['code']:
            self._log.write('FAILED: Unable to compress ' + str(inFile))

        if os.path.exists(tempFile):
            os.remove(tempFile)

        if not os.path.exists(outFile):
            self._log.write('FAILED: ' + target + ' -> ' + ofn)
            return False
        elif fileType == IncludeCompressor.JS_TYPE:
            f          = open(outFile, 'r')
            compressed = f.read()
            f.close()

            compressed = IncludeCompressor._REMOVE_COMMENT_RE.sub('', compressed)
            compressed = IncludeCompressor._REMOVE_COMMENT_LINE_RE.sub('', compressed)

            f = open(outFile, 'w')
            f.write(compressed.strip())
            f.close()

        inSize  = SizeUnits.SizeConversion.bytesToKilobytes(inFile, 2)
        outSize = SizeUnits.SizeConversion.bytesToKilobytes(outFile, 2)
        saved   = SizeUnits.SizeConversion.convertDelta(
            inSize, outSize, SizeUnits.SIZES.KILOBYTES, 2)

        self._log.write(
            'Compressed[%s]: %s -> %s [%sKB -> %sKB | Saved: %sKB]' % (
                fileType, target, ofn, inSize, outSize, saved))

        return True

#___________________________________________________________________________________________________ _compressInFolder
    def _compressInFolder(self, dumb, directory, names):
        if directory.find('.svn') != -1:
                return

        for fn in names:
            self._compressFile(fn, directory)


####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ usage
def usage():
    """ Compresses javascript or css using uglify JS compressor for deployment.
    -p | --path     - Root path used to pack javascript or css files.
    -c | --coffee   - Also compile coffeescript prior to compression."""

#___________________________________________________________________________________________________ main
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hp:cy", ["help", "path=", "coffee"])
    except getopt.GetoptError as err:
        print(str(err) + "\n")
        usage()
        sys.exit(2)

    path   = None
    coffee = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-p", "--path"):
            path = a
        elif o in ("-c", "--coffee"):
            coffee = True
        else:
            print("\nUnknown argument: " + o + ". Unable to continue.\n\n")
            usage()
            sys.exit(2)

    currentDirectory = os.path.abspath(os.curdir)
    if path is None:
        name, path = queryFromList(
            'Select the path you want compressed?', [
                'Current Directory: [%s]' % currentDirectory,
                'Other [enter custom value]' ],
            [currentDirectory, None ])
        if path is None:
            path = queryGeneralValue('Specify the path you want compressed?', currentDirectory)

    inc = IncludeCompressor(coffee)
    inc.compress(path)

    print("Operation complete.")

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    main()

