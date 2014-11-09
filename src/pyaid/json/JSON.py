# JSON.py
# (C)2011-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
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
        if encoding is None:
            encoding = 'utf-8'

        if pretty:
            kwargs = dict(separators=(',', ': '), indent=4, sort_keys=True)
        else:
            kwargs = dict(separators=(',', ':'))

        if sys.version < '3':
            kwargs['encoding'] = encoding

        try:
            return jsonint.dumps(src, **kwargs)
        except Exception:
            try:
                return jsonint.dumps(cls._reformat(src), **kwargs)
            except Exception:
                print('JSON Failed to encode:', src)
                raise

#___________________________________________________________________________________________________ fromString
    @classmethod
    def fromString(cls, src):
        if not src:
            return None
        return jsonint.loads(StringUtils.toUnicode(src))

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
            res = StringUtils.toStr2(cls.asString(value, pretty=pretty))
            if gzipped:
                f = gzip.open(path, 'wb')
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
        elif StringUtils.isStringType(value):
            value = StringUtils.toUnicode(value)
        elif isinstance(value, (list, tuple)):
            vout = []
            for item in value:
                vout.append(cls._reformatValue(item))
            value = vout
        return value
