# SizeUnits.py
# (C)2011-2012
# Scott Ernst

import os
import math
from decimal import Decimal
from operator import itemgetter

from pyaid.reflection.Reflection import Reflection

#___________________________________________________________________________________________________ SIZES
class SIZES(object):

#===================================================================================================
#                                                                                       C L A S S

    BYTES     = {'id':'B', 'bytes':1}
    KILOBYTES = {'id':'KB', 'bytes':1024}
    MEGABYTES = {'id':'MB', 'bytes':1048576}
    GIGABYTES = {'id':'GB', 'bytes':1073741824}
    TERABYTES = {'id':'TB', 'bytes':1099511627776}

#___________________________________________________________________________________________________ SizeConversion
class SizeConversion(object):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ convert
    @staticmethod
    def convertDelta(sizeOrFileA, sizeOrFileB, sizeEnum, roundDigits =-1):
        sizeA = SizeConversion.convert(sizeOrFileA, sizeEnum, SIZES.BYTES, -1)
        sizeB = SizeConversion.convert(sizeOrFileB, sizeEnum, SIZES.BYTES, -1)
        size  = sizeA - sizeB if sizeA > sizeB else sizeB - sizeA

        return SizeConversion.convert(size, SIZES.BYTES, sizeEnum, roundDigits)

#___________________________________________________________________________________________________ convert
    @staticmethod
    def convert(sizeOrFile, fromSizeEnum, toSizeEnum =None, roundDigits =-1):
        if toSizeEnum is None:
            toSizeEnum = SIZES.BYTES

        if hasattr(sizeOrFile, 'read') or isinstance(sizeOrFile, str):
            size         = SizeConversion.getSizeOfFile(sizeOrFile)
            fromSizeEnum = SIZES.BYTES
        else:
            size = sizeOrFile

        result = float(size)*float(fromSizeEnum['bytes'])/float(toSizeEnum['bytes'])
        if roundDigits < 0:
            return result
        else:
            return float(Decimal(str(result)).quantize(Decimal('1.' + ('0'*roundDigits))))

#___________________________________________________________________________________________________ prettyPrint
    @staticmethod
    def prettyPrint(size, sizeEnum =None, precision =-1):
        if hasattr(size, 'read') or isinstance(size, str):
            size = SizeConversion.getSizeOfFile(size)

        if size == 0:
            return '0B'

        sizeInBytes = float(size) if sizeEnum is None else float(size)*sizeEnum['bytes']
        sizeOptions = sorted(Reflection.getReflectionList(SIZES), key=itemgetter('bytes'))

        prev = None
        for opt in sizeOptions:
            if size < opt['bytes']:
                newSize = SizeConversion.convert(int(math.ceil(sizeInBytes)), SIZES.BYTES, prev)
                outSize = str(newSize)
                if precision != -1 and outSize.find('.') != -1:
                    parts   = outSize.split('.')
                    outSize = parts[0] + '.' + parts[1][:precision]

                return outSize + (prev['id'] if not prev is None else 'B')

            prev = opt

        return 'NaN'

#___________________________________________________________________________________________________ bytesToKilobytes
    @staticmethod
    def bytesToKilobytes(sizeInBytes, roundDigits =-1):
        return SizeConversion.convert(sizeInBytes, SIZES.BYTES, SIZES.KILOBYTES, roundDigits)

#___________________________________________________________________________________________________ bytesToMegabytes
    @staticmethod
    def bytesToMegabytes(sizeInBytes, roundDigits =-1):
        return SizeConversion.convert(sizeInBytes, SIZES.BYTES, SIZES.MEGABYTES, roundDigits)

#___________________________________________________________________________________________________ bytesToGigabytes
    @staticmethod
    def bytesToGigabytes(sizeInBytes, roundDigits =-1):
        return SizeConversion.convert(sizeInBytes, SIZES.BYTES, SIZES.GIGABYTES, roundDigits)

#___________________________________________________________________________________________________ bytesToTerabytes
    @staticmethod
    def bytesToTerabytes(sizeInBytes, roundDigits =-1):
        return SizeConversion.convert(sizeInBytes, SIZES.BYTES, SIZES.TERABYTES, roundDigits)

#___________________________________________________________________________________________________ getSizeOfFile
    @staticmethod
    def getSizeOfFile(fileOrFilename):
        if hasattr(fileOrFilename, 'read'):
            return os.path.getsize(fileOrFilename.name)
        elif isinstance(fileOrFilename, str):
            return os.path.getsize(fileOrFilename) if os.path.exists(fileOrFilename) else 0
