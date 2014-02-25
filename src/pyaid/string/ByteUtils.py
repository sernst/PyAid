# ByteUtils.py
# (C)2013-2014
# Scott Ernst

#___________________________________________________________________________________________________ ByteUtils
class ByteUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ getAsFourCC
    @classmethod
    def getAsFourCC(cls, value, isLittleEndian = False):
        res   = 0
        index = 0

        if isLittleEndian:
            while index < 4:
                res += ord(value[index]) << 8*index
                index += 1
            return res

        while index < 4:
            res += ord(value[3 - index]) << 8*index
            index += 1
        return res

#___________________________________________________________________________________________________ decodeFourCC
    @classmethod
    def decodeFourCC(cls, value, isLittleEndian = False):
        res   = ''
        index = 0

        if isLittleEndian:
            while index < 4:
                res += chr((value >> 8*index) & 0xFF)
                index += 1
            return res

        while index < 4:
            res += chr((value >> 8*(3 - index)) & 0xFF)
            index += 1
        return res

