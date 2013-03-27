# DataFormatConverter.py
# (C)2011
# Scott Ernst

import sys
import os
import getopt
import codecs

from pyaid.debug.Logger import Logger
from pyaid.interactive.queries import queryGeneralValue, queryFromList
from pyaid.xml.XMLConfigParser import XMLConfigParser
from pyaid.xml.JSONConfigParser import JSONConfigParser

#___________________________________________________________________________________________________ DataFormatConverter
class DataFormatConverter(object):
    """A class for converting between various data interchange formats, e.g. XML and JSON."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of ClassTemplate."""
        self._type = None
        self._src  = None
        self._log  = Logger('DataFormatConverter')
        self._path = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: propertyName
    @property
    def source(self):
        return self._src

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ load
    def load(self, path, fileType):
        if not os.path.exists(path):
            self._log.write('ERROR: Path does not exist [%s]. Unable to load.' % path)
            return False

        try:
            fh  = codecs.open(path, 'r', 'utf-8')
            res = fh.read()
            fh.close()
            enc = res.encode('utf-8')
            self.loads(enc, fileType)
        except Exception, err:
            self._log.writeError('Failed to load source file [%s].' % path, err)
            return False

        self._path = path
        return True

#___________________________________________________________________________________________________ load
    def loads(self, srcString, srcType):
        if srcString is None:
            self._log.write('ERROR: Source string is empty or invalid.')
            return False

        if isinstance(srcString, unicode):
            srcString = srcString.encode('utf-8')

        self._path = None
        self._src  = srcString
        self._type = srcType
        return True

#___________________________________________________________________________________________________ convertDirectory
    def convertDirectory(self, path, srcType, targetType, recursive =False):
        if srcType is None or targetType is None:
            self._log.write('ERROR: Source and/or target types are invalid. Operation aborted.')
            return False

        if not os.path.exists(path):
            self._log.write('ERROR: The specified path [%s] does not exist. Operation aborted.' \
                            % str(path))
            return False

        if recursive:
            os.path.walk(path, self._convertInDirectory, [srcType, targetType])
        else:
            self._convertInDirectory([srcType, targetType], path, os.listdir(path))

        return True

#___________________________________________________________________________________________________ writeToFile
    def writeToFile(self, targetType, path =None):
        if path is None and self._path is None:
            self._log.write('ERROR: Unable to write to file, no path was specified.')
            return False

        # Assign the reader based on source type
        reader = self._getParserFromType()
        if reader is None:
            self._log.write('ERROR: Unrecognized source type [%s]. Unable to convert.' % self._type)
            return False

        # Assign writer based on target type
        writer = self._getParserFromType(targetType)
        if writer is None:
            self._log.write('ERROR: Unrecognized conversion target type [%s]. Unable to convert.' \
                            % targetType)
            return False

        path = path if path else self._path
        d    = os.path.dirname(path)
        f    = os.path.basename(path).split('.')[0]
        f   += '.' + writer.TYPE_ID

        if not os.path.exists(d):
            os.makedirs(d)

        try:
            print len(self._src)
            src = reader.parse(self._src, None, True)
        except Exception, err:
            self._log.writeError('ERROR: Failed to parse source. Conversion aborted.', err)
            return False

        try:
            res = writer.serialize(src)
        except Exception, err:
            self._log.writeError('ERROR: Failed to serialized data. Conversion aborted.', err)
            return False

        out = os.path.join(d, f)
        try:
            fh = codecs.open(out, 'wb', 'utf-8')
            fh.write(res)
            fh.close()
        except Exception, err:
            self._log.writeError('ERROR: Failed to write file [%s]. Conversion aborted.' \
                                 % str(out), err)
            return False

        self._log.write('Converted: [%s] => [%s].' % (self._path, out))
        return True

#___________________________________________________________________________________________________ getAsXML
    def getAsXML(self):
        """Doc..."""
        if self._type == XMLConfigParser.TYPE_ID:
            return self._src
        else:
            return self._convert(XMLConfigParser.TYPE_ID)

#___________________________________________________________________________________________________ getAsJSON
    def getAsJSON(self):
        """Doc..."""
        if self._type == JSONConfigParser.TYPE_ID:
            return self._src
        else:
            return self._convert(JSONConfigParser.TYPE_ID)

#___________________________________________________________________________________________________ getAsDictionary
    def getAsDictionary(self, asInterchangeFormat =False):
        reader = self._getParserFromType()
        reader.parse(self._src, None, asInterchangeFormat)

#___________________________________________________________________________________________________ executeConversion
    @staticmethod
    def executeConversion(source =None, srcType =None, targetType =None, target =None, recursive =False):
        types = ['xml', 'json']

        if source is None:
            source = queryGeneralValue('Enter the source file (or path) to convert:')

        if srcType is None and os.path.isfile(source):
            fileType = source.split('.')[-1].lower()
            if fileType in types:
                srcType = fileType

        if srcType is None:
            srcType = queryFromList('Specify source file(s) type:', types)

        if targetType is None:
            targetType = queryFromList('Specify target file(s) type:', types)

        d = DataFormatConverter()
        if os.path.isfile(source):
            d.load(source, srcType)
            d.writeToFile(targetType, target)
        else:
            d.convertDirectory(source, srcType, targetType, recursive)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _convert
    def _convert(self, targetType):
        reader = self._getParserFromType()
        data   = reader.parse(self._src, None, True)

        if data is None:
            self._log.write('ERROR: Failed to parse input from. Skipping conversion.')
            return None

        writer = self._getParserFromType(targetType)
        return writer.serialize(data)

#___________________________________________________________________________________________________ _getParserFromType
    def _getParserFromType(self, typeID =None):
        if typeID is None:
            typeID = self._type

        if typeID == XMLConfigParser.TYPE_ID:
            return XMLConfigParser
        elif typeID == JSONConfigParser.TYPE_ID:
            return JSONConfigParser
        else:
            self._log.write('ERROR: _getParserFromType() failed for type: ' + str(typeID))
            return None

#___________________________________________________________________________________________________ _convertInDirectory
    def _convertInDirectory(self, types, dirname, names):
        if dirname.find('.svn') != -1:
            return

        reader = self._getParserFromType(types[0])
        writer = self._getParserFromType(types[1])
        for n in names:
            if not n.endswith(reader.TYPE_ID):
                continue

            src = os.path.join(dirname, n)
            self.load(src, reader.TYPE_ID)
            self.writeToFile(writer.TYPE_ID)

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ usage
def usage():
    print "Converts between various data formats (e.g. XML and JSON)"
    print "-o | --ouput       - Output type (either 'xml' or 'json')"
    print "-i | --input       - Input type (either 'xml' or 'json')"
    print "-s | --source      - Source file or path to convert all source files within a path."
    print "-t | --target      - Target (output) path to write converted files to. By default they"
    print "                     will be written in the same folder as the source file."
    print "-r | --recursive   - Recurse into subdirectories."

#___________________________________________________________________________________________________ main
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "ho:i:s:rt:", [
            "help", "output=", "input=", "source=", "recursive", "target="
        ])
    except getopt.GetoptError, err:
        print str(err) + "\n"
        usage()
        sys.exit(2)

    srcType    = None
    targetType = None
    source     = None
    target     = None
    recursive  = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            targetType = a
        elif o in ("-i", "--input"):
            srcType = a
        elif o in ("-s", "--source"):
            source = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-r", "--recursive"):
            recursive = True
        else:
            print "\nUnknown argument: " + o + ". Unable to continue.\n\n"
            usage()
            sys.exit(2)

    DataFormatConverter.executeConversion(source, srcType, targetType, target, recursive)
    print "\n\nConversion operation complete.\n"

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    main()
