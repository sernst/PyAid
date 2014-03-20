# ByteChunk.py
# (C)2013-2014
# Scott Ernst

import math
import struct
import zlib

from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils

from pyaid.string.ByteUtils import ByteUtils

#___________________________________________________________________________________________________ ByteChunk
class ByteChunk(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    BIG_ENDIAN      = '>'
    LITTLE_ENDIAN   = '<'

#___________________________________________________________________________________________________ __init__
    def __init__(self, endianess = None, sourceBytes = None):
        """Creates a new instance of ByteChunk."""
        self._data      = sourceBytes if sourceBytes is not None else bytearray()
        self._endianess = endianess if endianess else self.LITTLE_ENDIAN
        self._position  = 0

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: byteArray
    @property
    def byteArray(self):
        return self._data

#___________________________________________________________________________________________________ GS: isEmpty
    @property
    def isEmpty(self):
        return self.length == 0

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        return len(self._data)

#___________________________________________________________________________________________________ GS: bytesLeft
    @property
    def bytesLeft(self):
        return self.length - self.position
    @bytesLeft.setter
    def bytesLeft(self, value):
        self.position = value

#___________________________________________________________________________________________________ GS: position
    @property
    def position(self):
        return max(0 , min(self.length, self._position))
    @position.setter
    def position(self, value):
        self._position = max(0, min(self.length, value))

#___________________________________________________________________________________________________ GS: endianess
    @property
    def endianess(self):
        return self._endianess if self._endianess else self.LITTLE_ENDIAN
    @endianess.setter
    def endianess(self, value):
        self._endianess = value

#___________________________________________________________________________________________________ GS: isLittleEndian
    @property
    def isLittleEndian(self):
        return self.endianess == self.LITTLE_ENDIAN
    @isLittleEndian.setter
    def isLittleEndian(self, value):
        self.endianess = self.LITTLE_ENDIAN if value else self.BIG_ENDIAN

#___________________________________________________________________________________________________ GS: isBigEndian
    @property
    def isBigEndian(self):
        return self.endianess == self.BIG_ENDIAN
    @isBigEndian.setter
    def isBigEndian(self, value):
        self.endianess = self.BIG_ENDIAN if value else self.BIG_ENDIAN

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ writeBytes
    def writeBytes(self, ba):
        if self._position >= self.length - 1:
            self._data += ba
            self._position = self.length - 1
            return

        end = self._position + len(ba)
        self._data = self._data[:self._position] + ba + self._data[end:]
        self._position = end

#___________________________________________________________________________________________________ writeByte
    def writeByte(self, value):
        if self._position >= self.length - 1:
            self._data.append(value)
            self._position = self.length - 1
        else:
            self._data[self._position] = value
            self._position += 1

#___________________________________________________________________________________________________ writeChunk
    def writeChunk(self, chunk):
        self.writeBytes(chunk.byteArray)

#___________________________________________________________________________________________________ writeString
    def writeString(self, value):
        self.writeBytes(bytes(StringUtils.unicodeToStr(value)))
        # self.writeBytes(struct.pack(self.endianess + 's', StringUtils.unicodeToStr(value)))

#___________________________________________________________________________________________________ writeUint8
    def writeUint8(self, value):
        """ Write an unsigned 8bit integer."""
        self.writeByte(value & 0xFF)

#___________________________________________________________________________________________________ writeInt8
    def writeInt8(self, value):
        """ Read a signed 8bit integer."""
        self.writeByte(struct.pack('b', int(value)))

#___________________________________________________________________________________________________ writeInt16
    def writeInt16(self, value):
        self.writeBytes(struct.pack(self.endianess + 'h', int(value)))

#___________________________________________________________________________________________________ writeUint16
    def writeUint16(self, value):
        self.writeBytes(struct.pack(self.endianess + 'H', int(value)))

#___________________________________________________________________________________________________ writeUint24
    def writeUint24(self, value):
        if self.isBigEndian:
            self.writeUint16((value >> 8) & 0xFFFF)
            self.writeByte(value & 0xFF)
            return

        self.writeByte(value & 0xFF)
        self.writeByte(value & 0xFF00)
        self.writeByte(value & 0xFF0000)

#___________________________________________________________________________________________________ writeInt32
    def writeInt32(self, value):
        self.writeBytes(struct.pack(self.endianess + 'i', int(value)))

#___________________________________________________________________________________________________ writeUint32
    def writeUint32(self, value):
        self.writeBytes(struct.pack(self.endianess + 'I', int(value)))

#___________________________________________________________________________________________________ writeInt64
    def writeInt64(self, value):
        self.writeBytes(struct.pack(self.endianess + 'q', int(value)))

#___________________________________________________________________________________________________ writeUint64
    def writeUint64(self, value):
        self.writeBytes(struct.pack(self.endianess + 'Q', int(value)))

#___________________________________________________________________________________________________ writFourCC
    def writeFourCC(self, fourCC):
        if isinstance(fourCC, basestring):
            fourCC = ByteUtils.getAsFourCC(fourCC, self.isLittleEndian)
        self.writeUint32(fourCC)

#___________________________________________________________________________________________________ writeFixedFloat32
    def writeFixedFloat32(self, value, fractionalSize = 16):
        """ Writes a 32-bit fixed-point number with the specified fractional bit size """
        self.writeInt32(int(round(value*float(math.pow(2, fractionalSize)))))

#___________________________________________________________________________________________________ writeFixedUfloat32
    def writeFixedUfloat32(self, value, fractionalSize = 16):
        """ Writes a 32-bit unsigned fixed-point number with the specified fractional bit size """
        self.writeUint32(int(round(value*float(math.pow(2, fractionalSize)))))

#___________________________________________________________________________________________________ writeFixedFloat16
    def writeFixedFloat16(self, value, fractionalSize = 8):
        """ Writes a 16-bit fixed-point number with the specified fractional bit size """
        self.writeInt16(int(round(value*float(math.pow(2, fractionalSize)))))

#___________________________________________________________________________________________________ writeFixedUfloat16
    def writeFixedUfloat16(self, value, fractionalSize = 8):
        """ Writes a 16-bit unsigned fixed-point number with the specified fractional bit size """
        self.writeUint16(int(round(value*float(math.pow(2, fractionalSize)))))

#___________________________________________________________________________________________________ readFixedFloat32
    def readFixedFloat32(self, fractionalSize = 16):
        """ Reads a 32-bit fixed-point number with the specified fractional bit size """
        return float(self.readInt32())/float(math.pow(2, fractionalSize))

#___________________________________________________________________________________________________ readFixedUfloat32
    def readFixedUfloat32(self, fractionalSize = 16):
        """ Reads a 32-bit unsigned fixed-point number with the specified fractional bit size """
        return float(self.readUint32())/float(math.pow(2, fractionalSize))

#___________________________________________________________________________________________________ readFixedFloat16
    def readFixedFloat16(self, fractionalSize = 8):
        """ Reads a 16-bit fixed-point number with the specified fractional bit size """
        return float(self.readInt16())/float(math.pow(2, fractionalSize))

#___________________________________________________________________________________________________ readFixedUfloat16
    def readFixedUfloat16(self, fractionalSize = 8):
        """ Reads a 16-bit unsigned fixed-point number with the specified fractional bit size """
        return float(self.readUint16())/float(math.pow(2, fractionalSize))

#___________________________________________________________________________________________________ readFourCCAsString
    def readFourCCAsString(self):
        return ByteUtils.decodeFourCC(self.read(4), self.isLittleEndian)

#___________________________________________________________________________________________________ read
    def read(self, length = -1):
        if not length:
            return ''
        start = self.position
        if length < 0:
            self.position = self.length + length + 1
        else:
            self.position += length
        return self._data[start:self.position].decode('utf-8')

#___________________________________________________________________________________________________ seek
    def seek(self, position):
        self.position = min(len(self._data) - 1, max(0, position))

#___________________________________________________________________________________________________ unpack
    def unpack(self, dataType, length):
        data = self.read(length)

        assert len(data) == length, \
            u"[UNPACK ERROR]: Unexpected end of stream [%s | %s]" % (
                unicode(len(data)), unicode(length))

        try:
            return struct.unpack(self.endianess + dataType, data)[0]
        except struct.error:
            print len(data)
            print u"Unable to unpack '%r'" % data
            raise

#___________________________________________________________________________________________________ readFloat32
    def readFloat32(self):
        """ Read a 32bit float."""
        return self.unpack('f', 4)

#___________________________________________________________________________________________________ readQuickTimeFloat32
    def readQuickTimeFloat32(self):
        """ Read a 32bit QuickTime float."""
        return self.readInt16() + float(self.readUint16()) /65535

#___________________________________________________________________________________________________ readQuickTimeUnsignedFloat32
    def readQuickTimeUnsignedFloat32(self):
        """ Read a 32bit QuickTime float."""
        return self.readUint16() + float(self.readUint16()) /65535

#___________________________________________________________________________________________________ readUint64
    def readUint64(self):
        """ Read an unsigned 64bit integer."""
        return self.unpack('Q', 8)

#___________________________________________________________________________________________________ readInt64
    def readInt64(self):
        """ Read an signed 64bit integer."""
        return self.unpack('q', 4)

#___________________________________________________________________________________________________ readUint32
    def readUint32(self):
        """ Read an unsigned 32bit integer."""
        return self.unpack('I', 4)

#___________________________________________________________________________________________________ readInt32
    def readInt32(self):
        """ Read an signed 32bit integer."""
        return self.unpack('i', 4)

#___________________________________________________________________________________________________ readUint16
    def readUint16(self):
        """ Read an unsigned 16bit integer."""
        return self.unpack('H', 2)

#___________________________________________________________________________________________________ readInt16
    def readInt16(self):
        """ Read an signed 16bit integer."""
        return self.unpack('h', 2)

#___________________________________________________________________________________________________ readUint24
    def readUint24(self):
        if self.isBigEndian:
            return (self.readUint16() << 8) + self.readUint8()

        return self.readUint8() + (self.readUint8() << 8) + (self.readUint8() << 16)

#___________________________________________________________________________________________________ readInt24
    def readInt24(self):
        if self.isBigEndian:
            return (self.readInt16() << 8) + self.readUint8()

        return self.readUint8() + (self.readUint8() << 8) + (self.readInt8() << 16)

#___________________________________________________________________________________________________ readUint8
    def readUint8(self):
        """ Read an unsigned 8bit integer."""
        return ord(self.read(1))

#___________________________________________________________________________________________________ readInt8
    def readInt8(self):
        """ Read a signed 8bit integer."""
        return struct.unpack('b', self.read(1))[0]

#___________________________________________________________________________________________________ readDWord
    def readDWord(self):
        return self.read(4)

#___________________________________________________________________________________________________ readWord
    def readWord(self):
        return self.read(2)

#___________________________________________________________________________________________________ readQWord
    def readQWord(self):
        return self.read(8)

#___________________________________________________________________________________________________ readByte
    def readByte(self):
        return self.read(1)

#___________________________________________________________________________________________________ readFourCC
    def readFourCC(self):
        return self.read(4)

#___________________________________________________________________________________________________ clear
    def clear(self):
        self._data    = bytearray()
        self.position = 0

#___________________________________________________________________________________________________ toFile
    def toFile(self, path):
        path = FileUtils.cleanupPath(path, isFile=True)

        try:
            f = open(path, 'wb')
            f.write(self._data)
            f.close()
        except Exception, err:
            print 'FAILED: Write ByteChunk to file'
            raise

#___________________________________________________________________________________________________ compress
    def compress(self, level =6):
        self._data = bytearray(zlib.compress(bytes(self._data), level))

#___________________________________________________________________________________________________ uncompress
    def uncompress(self):
        self._data = bytearray(zlib.decompress(bytes(self._data)))

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

