# StringUtils.py
# (C)2011-2014
# Scott Ernst and Eric David Wills

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import re
import sys
import string
import random
import math
import unicodedata
import textwrap

if sys.version < '3':
    # noinspection PyUnresolvedReferences
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

#___________________________________________________________________________________________________ StringUtils
class StringUtils(object):
    """ A class for string related operations, targeting both byte and unicode strings, but
        focusing primarily on unicode strings for forward compatibility. """

    TEXT_TYPE   = text_type
    BINARY_TYPE = binary_type

#===================================================================================================
#                                                                                     P U B L I C

    HTML_ESCAPE_CODES = [
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
        ('$', '&#36;'),
        ('\u201d', '&quot;'),
        ('\u201c', '&quot;') ]

    _SOLO_BACKSLASH_PATTERN = re.compile('(?<!\\\)\\\(?!\\\)')

#___________________________________________________________________________________________________ isTextType
    @classmethod
    def isTextType(cls, source):
        """isTextType doc..."""
        return isinstance(source, text_type)

#___________________________________________________________________________________________________ isBinaryType
    @classmethod
    def isBinaryType(cls, source):
        """isBinaryType doc..."""
        return isinstance(source, binary_type)

#___________________________________________________________________________________________________ dedent
    @classmethod
    def dedent(cls, source, collapse =True):
        """ Removes indentation from the source string. If collapse is true then line breaks are
            also removed. """
        out = textwrap.dedent(source.strip('\r\n')).replace('\r', '').strip()
        if collapse:
            return out.replace('\n', ' ')
        return out

#___________________________________________________________________________________________________ unichr
    @classmethod
    def unichr(cls, source):
        """unichr doc..."""
        if sys.version > '3':
            return chr(source)
        # noinspection PyUnresolvedReferences
        return unichr(source)

#___________________________________________________________________________________________________ isStringType
    @classmethod
    def isStringType(cls, value, strict =False):
        """isString doc..."""
        if strict:
            return isinstance(value, text_type)
        return isinstance(value, (text_type, binary_type))

#___________________________________________________________________________________________________ capitalizeWords
    @classmethod
    def capitalizeWords(cls, source):
        """capitalizeWords doc..."""
        try:
            return source.title()
        except Exception:
            return text_type(source).title()

#___________________________________________________________________________________________________ source
    @classmethod
    def slugify(cls, source):
        """ Normalizes string, converts to lowercase, removes non-alpha characters,
            and converts spaces to hyphens. Useful in creating safe filenames. """

        source = cls.toUnicode(
            unicodedata.normalize('NFKD', cls.toUnicode(source)).encode('ascii', 'ignore'))
        return cls.toUnicode(re.sub('[^\w\s-]', '', source).strip().lower())

#___________________________________________________________________________________________________ matches
    @classmethod
    def matches(cls, source, test):
        """ Returns whether or not the source string matches the test string or any of the elements
            in a list of test strings. """

        if isinstance(test, binary_type):
            test = text_type(test)
            return source == test

        if isinstance(test, text_type):
            return source == test

        for item in test:
            if source == item:
                return True

        return False

#___________________________________________________________________________________________________ contains
    @staticmethod
    def contains(source, test, offset =0):
        """ Determines whether or not the string contains the specified test string or list of
            possible test strings.

            @@@param source:string
                The source string on which to test.

            @@@param test:string,list
                A string to test or a list of strings to test. If test is a list the method will
                return True if any of the strings in the list are a match.

            @@@returns bool
                Whether or not the string contains the test.
        """

        if isinstance(test, (text_type, binary_type)):
            return source.find(test, offset) != -1

        for t in test:
            if source.find(t, offset) != -1:
                return True

#___________________________________________________________________________________________________ containsAll
    @staticmethod
    def containsAll(source, test, offset =0):
        """ Determines whether or not the string contains the specified test string or list of
            possible test strings.

            @@@param source:string
                The source string on which to test.

            @@@param test:string,list
                A string to test or a list of strings to test. If test is a list the method will
                return True only if all of the strings in the list are a match.

            @@@returns bool
                Whether or not the string contains the test.
        """

        if isinstance(test, (text_type, binary_type)):
            return source.find(test, offset) != -1

        for t in test:
            if source.find(t, offset) == -1:
                return False

        return True

#___________________________________________________________________________________________________ begins
    @staticmethod
    def begins(source, test):
        """ Determines whether or not the string begins with the specified test string or list of
            possible test strings.

            @@@param source:string
                The source string on which to test.

            @@@param test:string,list
                A string to test or a list of strings to test. If test is a list the method will
                return True if any of the strings in the list are a match.

            @@@returns bool
                Whether or not the string begins with the test.
        """

        if isinstance(test, (text_type, binary_type)):
            return source.startswith(test)

        for t in test:
            if source.startswith(t):
                return True

        return False

#___________________________________________________________________________________________________ ends
    @staticmethod
    def ends(source, test):
        """ Determines whether or not the string ends with the specified test string or list of
            possible test strings.

            @@@param source:string
                The source string on which to test.

            @@@param test:string,list
                A string to test or a list of strings to test. If test is a list the method will
                return True if any of the strings in the list are a match.

            @@@returns bool
                Whether or not the string ends with the test.
        """

        if isinstance(test, (text_type, binary_type)):
            return source.endswith(test)

        for t in test:
            if source.endswith(t):
                return True

        return False

#___________________________________________________________________________________________________ getRandomString
    @staticmethod
    def getRandomString(length):
        choices = string.ascii_letters + '012345689'
        res     = ''

        for i in range(0, length):
            res += random.choice(choices)

        return res

#___________________________________________________________________________________________________ getAsUID
    @staticmethod
    def getAsUID(source, preserveCase =False):
        """ From the input source string, convert it to a valid UID, which removes illegal
            characters from the string and formats it in lower case.

            @@@param source:string
                The source string to modify.

            @@@param preserveCase:bool -default:False
                If True the uid will preserve case. Used primarily for display purposes, this property
                should remain False for database related activity.

            @@@returns string
                The source string formatted as a UID.
        """

        out = re.compile('[^A-Za-z0-9_]').sub('', source)
        return text_type(out if preserveCase else out.lower())

#___________________________________________________________________________________________________ abbreviate
    @staticmethod
    def abbreviate(text, length, truncation ='...', sepChar =' '):
        if len(text) <= length:
            return text

        if not truncation:
            truncation = ''

        parts  = text.split(sepChar)
        output = parts[0]
        index  = 1
        while len(output) < length:
            lenOut   = len(output)
            lenPart  = len(parts[index])
            nextLen  = lenOut + lenPart
            nowFill  = abs(length - lenOut)
            nextFill = abs(length - lenOut - lenPart)
            if nextLen > length and nowFill < 2*len(truncation):
                break
            if nextFill < nowFill:
                output += sepChar + parts[index]
                index  += 1
            else:
                break

        end = int(max(length - len(truncation), 0))
        return output[:end] + truncation

#___________________________________________________________________________________________________ abbreviateRight
    @classmethod
    def abbreviateRight(cls, text, length, truncation ='...', sepChar =' '):
        if len(text) <= length:
            return text

        if not truncation:
            truncation = ''

        parts  = text.split(sepChar)
        output = parts[-1]
        index  = -2
        while len(output) < length:
            lenOut   = len(output)
            lenPart  = len(parts[index])
            nextLen  = lenOut + lenPart
            nowFill  = abs(length - lenOut)
            nextFill = abs(length - lenOut - lenPart)
            if nextLen > length and nowFill < 2*len(truncation):
                break
            if nextFill < nowFill:
                output = parts[index] + sepChar + output
                index  -= 1
            else:
                break
        start = int(max(0, len(output) - length - len(truncation)))
        return truncation + output[start:]

#___________________________________________________________________________________________________ abbreviateCenter
    @classmethod
    def abbreviateCenter(cls, text, length, truncation ='...', sepChar =' '):
        if len(text) <= length:
            return text

        halfLength = math.floor(0.5*float(length))
        left  = cls.abbreviate(text, halfLength, '', sepChar=sepChar)
        right = cls.abbreviateRight(text, length - halfLength, '', sepChar=sepChar)

        return left + truncation + right

#___________________________________________________________________________________________________ abbreviatePath
    @classmethod
    def abbreviatePath(cls, path, length, truncation ='...'):
        if len(path) <= length:
            return path
        p = path.replace('\\', '/')
        return cls.abbreviateCenter(p, length, truncation, sepChar='/').replace('/', os.sep)

#___________________________________________________________________________________________________ camelCapsToWords
    @staticmethod
    def camelCapsToWords(source, capitalize =False):
        if not source or not isinstance(source, (text_type, binary_type)):
            return ''

        out = source.replace('-', ' ').replace('_', ' ').strip()
        out = re.compile('([a-z])([A-Z0-9])').sub('\g<1> \g<2>', out)
        out = re.compile('([A-Z0-9])([A-Z0-9])([a-z])').sub('\g<1> \g<2>\g<3>', out)
        out = out.strip()

        if capitalize:
            index = 0
            while index != -1:
                index = out.find(' ', index)
                if index == -1:
                    break

                out    = out[:index+1] + out[index+1].upper() + out[index+2:]
                index += 1

            out = out[0].upper() + out[1:]
        else:
            out = out.lower()

        return out

#___________________________________________________________________________________________________ htmlEscape
    @staticmethod
    def htmlEscape(source, additionalEscapes =None):

        escapes = StringUtils.HTML_ESCAPE_CODES
        if additionalEscapes:
            if isinstance(additionalEscapes, dict):
                additionalEscapes = additionalEscapes.items()

            escapes = escapes + additionalEscapes

        for esc in escapes:
            source = source.replace(esc[0], esc[1])

        return source

#___________________________________________________________________________________________________ escapeBackSlashes
    @classmethod
    def escapeBackSlashes(cls, source, soloOnly =True):
        if soloOnly:
            return cls._SOLO_BACKSLASH_PATTERN.sub('\\\\\\\\', source)
        return source.replace('\\', '\\\\')

#___________________________________________________________________________________________________ getCompleteFragment
    @staticmethod
    def getCompleteFragment(source, maxLength =-1, preferSentences =False, addEllipsis =True):
        if not source or not isinstance(source, (text_type, binary_type)):
            return ''

        if maxLength < 0:
            maxLength = len(source)

        source = source.strip()

        # SENTENCES
        if preferSentences:
            frag = source[:maxLength]
            if frag.endswith('.') or frag.endswith('!') or frag.endswith('?'):
                return frag

            index = max(
                frag.rfind('. ', 0, maxLength),
                frag.rfind('! ', 0, maxLength),
                frag.rfind('? ', 0, maxLength)
            )
            if index != -1 and index > round(0.5*maxLength):
                return frag[:index+1]

        if len(source) <= maxLength:
            return source + ('...' if addEllipsis and preferSentences else '')

        if source[maxLength+1] == ' ':
            return source[:maxLength] + ('...' if addEllipsis else '')

        # WORDS
        index = source.rfind(' ', 0, maxLength)
        if index != -1:
            return source[:index] + ('...' if addEllipsis else '')

        return source[:maxLength] + ('...' if addEllipsis else '')

#___________________________________________________________________________________________________ extendToLength
    @classmethod
    def extendToLength(cls, value, length, char =' ', clip =False):
        """ Extends the length of the string to the specified length using the specified character """
        if value is None:
            return None

        if not cls.isStringType(value):
            value = StringUtils.toText(value)

        if not value:
            return length*char

        vLen = len(value)
        if vLen == length:
            return value
        elif vLen > length:
            return value[:length] if clip else value

        return value + char*(length - vLen)

#___________________________________________________________________________________________________ checkIsEmailAddress
    @classmethod
    def checkIsEmailAddress(cls, value):
        return re.match(
            '^.+@[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,}|[0-9]{1,3})$', value
        ) is not None


#___________________________________________________________________________________________________ strToUnicode
    @classmethod
    def strToUnicode(cls, value, force =False):
        if isinstance(value, cls.TEXT_TYPE):
            return value

        if not isinstance(value, cls.BINARY_TYPE):
            if not force:
                return value
            if value is None:
                return 'None'
            value = cls.TEXT_TYPE(value)

        try:
            if sys.version < '3':
                return value.decode('utf8', 'ignore')
            else:
                return value.decode('utf8')
        except Exception:
            return value

#___________________________________________________________________________________________________ unicodeToStr
    @classmethod
    def unicodeToStr(cls, value, force =False):
        if isinstance(value, cls.BINARY_TYPE):
            return value

        if not isinstance(value, cls.TEXT_TYPE):
            if not force:
                return value
            if value is None:
                return cls.BINARY_TYPE('None')
            value = cls.BINARY_TYPE(value)

        try:
            if sys.version < '3':
                return value.encode('utf8', 'ignore')
            else:
                return cls.BINARY_TYPE(value, 'utf8')
        except Exception:
            return value

#___________________________________________________________________________________________________ zeroFill
    @classmethod
    def zeroFill(cls, source, length):
        return cls.toText(source).zfill(length)

#___________________________________________________________________________________________________ leftPad
    @classmethod
    def leftPad(cls, source, padChar):
        """leftPad doc..."""
        while len(source) < padChar:
            source = padChar + source
        return source

#___________________________________________________________________________________________________ toUnicode
    @classmethod
    def toUnicode(cls, value):
        """toUnicode doc..."""
        return cls.strToUnicode(value, force=True)

#___________________________________________________________________________________________________ toStr2
    @classmethod
    def toStr2(cls, value, force =False):
        """toStr2 doc..."""
        if sys.version > '3':
            return value

        return cls.unicodeToStr(value, force=force)

#___________________________________________________________________________________________________ toStr
    @classmethod
    def toStr(cls, value):
        """toStr doc..."""
        return cls.unicodeToStr(value, force=True)

#___________________________________________________________________________________________________ toBytes
    @classmethod
    def toBytes(cls, value):
        """toBytes doc..."""
        return cls.unicodeToStr(value, force=True)

#___________________________________________________________________________________________________ toText
    @classmethod
    def toText(cls, value):
        """toText doc..."""
        return cls.strToUnicode(value, force=True)

#___________________________________________________________________________________________________ toStrStr
    @classmethod
    def toStrStr(cls, value, force =False):
        """ In Python 2 this will convert unicodes to strings and in Python 3 it will convert
            bytes to strings. Either way you get a str(). If not force then non text/binary
            types will be returned unchanged. Otherwise, they will be converted to a text/binary
            type. """

        if sys.version > '3':
            return cls.strToUnicode(value, force=force)
        return cls.unicodeToStr(value, force=force)
