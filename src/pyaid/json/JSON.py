# JSON.py
# (C)2011-2013
# Scott Ernst

import json
import gzip

#___________________________________________________________________________________________________ JSON
class JSON(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ asString
    @classmethod
    def asString(cls, src, pretty =False):
        """Doc..."""
        if pretty:
            return cls._dumpsPretty(src)
        return cls._dumpsCompact(src)

#___________________________________________________________________________________________________ fromString
    @classmethod
    def fromString(cls, src):
        return json.loads(src)

#___________________________________________________________________________________________________ fromFile
    @classmethod
    def fromFile(cls, path, gzipped =False, throwError =False):
        try:
            if gzipped:
                f = gzip.open(path, 'r+')
            else:
                f = open(path, 'r+')
            res = f.read()
            f.close()
            return cls.fromString(res.decode('utf-8', 'ignore'))
        except Exception, err:
            if throwError:
                raise
            else:
                print err
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
        except Exception, err:
            if throwError:
                raise
            else:
                print err
            return False

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _dumpsCompact
    @classmethod
    def _dumpsCompact(cls, src):
        return json.dumps(src, separators=(',', ':'))

#___________________________________________________________________________________________________ _dumpsPretty
    @classmethod
    def _dumpsPretty(cls, src):
        return json.dumps(src, separators=(',', ': '), indent=4, sort_keys=True)
