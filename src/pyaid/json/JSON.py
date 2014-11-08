# JSON.py
# (C)2011-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import json as jsonint
import gzip
from pyaid.dict.DictUtils import DictUtils

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ JSON
class JSON(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ asString
    @classmethod
    def asString(cls, src, pretty =False, encoding =None):
        """Doc..."""
        if pretty:
            return cls._dumpsPretty(src, encoding=encoding)
        return cls._dumpsCompact(src, encoding=encoding)

#___________________________________________________________________________________________________ fromString
    @classmethod
    def fromString(cls, src):
        return jsonint.loads(StringUtils.strToUnicode(src))

#___________________________________________________________________________________________________ fromFile
    @classmethod
    def fromFile(cls, path, gzipped =False, throwError =False):
        try:
            if gzipped:
                f = gzip.open(path, 'rb')
            else:
                f = open(path, 'r')
            res = f.read()
            f.close()
            return cls.fromString(res)
        except Exception as err:
            if throwError:
                raise
            else:
                print(err)
            return None

#___________________________________________________________________________________________________ toFile
    @classmethod
    def toFile(cls, path, value, pretty =False, gzipped =False, throwError =False):
        try:
            res = cls.asString(value, pretty=pretty).encode('utf-8', 'ignore')
            if gzipped:
                f = gzip.open(path, 'w+')
            else:
                f = open(path, 'w+')
            f.write(res)
            f.close()
            return True
        except Exception as err:
            if throwError:
                raise
            else:
                print(err)
            return False

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _dumpsCompact
    @classmethod
    def _dumpsCompact(cls, src, encoding =None):
        if encoding is None:
            encoding = 'utf-8'

        try:
            return jsonint.dumps(src, separators=(',', ':'), encoding=encoding)
        except Exception:
            try:
                src = cls._reformat(src)
                return jsonint.dumps(src, separators=(',', ':'), encoding=encoding)
            except Exception:
                print('JSON Failed to encode:', src)
                raise

#___________________________________________________________________________________________________ _dumpsPretty
    @classmethod
    def _dumpsPretty(cls, src, encoding =None):
        if encoding is None:
            encoding = 'utf-8'

        try:
            return jsonint.dumps(
                src, separators=(',', ': '), indent=4, sort_keys=True, encoding=encoding)
        except Exception:
            try:
                src = cls._reformat(src)
                return jsonint.dumps(
                    src, separators=(',', ': '), sort_keys=True, encoding=encoding)
            except Exception:
                print('JSON Failed to encode:', src)
                raise

#___________________________________________________________________________________________________ _reformat
    @classmethod
    def _reformat(cls, src):
        out = dict()
        for n,v in DictUtils.iter(src):
            n = StringUtils.strToUnicode(n)

            out[n] = cls._reformatValue(v)
        return out

#___________________________________________________________________________________________________ _reformatValue
    @classmethod
    def _reformatValue(cls, value):
        if isinstance(value, dict):
            value = cls._reformat(value)
        elif isinstance(value, str):
            value = StringUtils.strToUnicode(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            vout = []
            for item in value:
                vout.append(cls._reformatValue(item))
            value = vout
        return value
