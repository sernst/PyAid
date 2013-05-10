# JSON.py
# (C)2011
# Scott Ernst

import json

#___________________________________________________________________________________________________ JSON
class JSON(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ asString
    @staticmethod
    def asString(src):
        """Doc..."""
        return json.dumps(src, separators=(',', ':'))

#___________________________________________________________________________________________________ fromString
    @staticmethod
    def fromString(src):
        return json.loads(src)

#___________________________________________________________________________________________________ fromFile
    @classmethod
    def fromFile(cls, path):
        try:
            f   = open(path, 'r+')
            res = f.read()
            f.close()
            return cls.fromString(res.decode('utf-8', 'ignore'))
        except Exception, err:
            print err
            return None

#___________________________________________________________________________________________________ toFile
    @classmethod
    def toFile(cls, path, value):
        try:
            res = cls.asString(value).encode('utf-8', 'ignore')
            f   = open(path, 'w+')
            f.write(res)
            f.close()
            return True
        except Exception, err:
            print err
            return False
