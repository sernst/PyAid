# ListUtils.py
# (C)2011-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys

from operator import itemgetter
from operator import attrgetter

from pyaid.string.StringUtils import StringUtils


# AS NEEDED: from pyaid.dict.DictUtils import DictUtils

#___________________________________________________________________________________________________ ListUtils
class ListUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ range
    @classmethod
    def range(cls, *args, **kwargs):
        """ Returns the generator form of the range, which differs between Python 2 and 3. """
        if sys.version < '3':
            return xrange(*args, **kwargs)
        return range(*args, **kwargs)

#___________________________________________________________________________________________________ prettyPrintBullets
    @classmethod
    def prettyPrintBullets(cls, source, indent ='  ', indentLevel =0, bullet ='*'):
        """prettyPrintBullets doc..."""
        source = cls.prettyPrint(source, separator='\n').strip('[]').split('\n')
        prefix = indentLevel*indent + bullet + ' '
        return prefix + prefix.join(source)

#___________________________________________________________________________________________________ prettyPrint
    @classmethod
    def prettyPrint(cls, source, separator = ', '):
        """prettyPrint doc..."""
        out = []

        from pyaid.dict.DictUtils import DictUtils

        for v in source:
            if isinstance(v, (list, tuple)):
                v = cls.prettyPrint(v, separator=',')
            if isinstance(v, dict):
                v = DictUtils.prettyPrint(v)
            elif isinstance(v, StringUtils.BINARY_TYPE):
                v = StringUtils.strToUnicode(v)
            else:
                v = StringUtils.toUnicode(v)
            out.append(v)

        return '[%s]' % separator.join(out)

#___________________________________________________________________________________________________ cleanBytesToText
    @classmethod
    def cleanBytesToText(cls, source, inPlace =True):
        """cleanBytesToText doc..."""

        out = source if inPlace else []
        from pyaid.dict.DictUtils import DictUtils
        for i in range(len(source)):
            v = source[i]
            if isinstance(v, (tuple, list)):
                v = cls.cleanBytesToText(v, inPlace=inPlace)
            elif isinstance(v, dict):
                v = DictUtils.cleanBytesToText(v, inPlace=inPlace)
            else:
                v = StringUtils.strToUnicode(v, force=False)

            if inPlace:
                out[i] = v
            else:
                out.append(v)

        return out

#___________________________________________________________________________________________________ asList
    @classmethod
    def asList(cls, target, allowTuples =True):
        """ Doc... """
        if isinstance(target, list):
            return target
        elif isinstance(target, tuple):
            return target if allowTuples else list(target)
        elif target is None:
            return []
        return [target]

#___________________________________________________________________________________________________ asTuple
    @classmethod
    def asTuple(cls, target, allowLists =True):
        if isinstance(target, tuple):
            return target
        elif isinstance(target, list):
            return target if allowLists else tuple(target)
        elif target is None:
            return None
        return target,

#___________________________________________________________________________________________________ itemsToString
    @classmethod
    def itemsToString(cls, target, inPlace =False, toUnicode =True):
        """ Iterates through the elements of the target list and converts each of them to binary
            strings, including decoding unicode strings to byte strings."""

        from pyaid.string.StringUtils import StringUtils

        output = target if inPlace else (target + [])
        index  = 0

        while index < len(target):
            source = target[index]
            if StringUtils.isStringType(source):
                if toUnicode:
                    output[index] = StringUtils.strToUnicode(source)
                else:
                    output[index] = StringUtils.unicodeToStr(source, force=True)
            else:
                output[index] = str(source)
            index += 1

        return output

#___________________________________________________________________________________________________ itemsToUnicode
    @classmethod
    def itemsToUnicode(cls, target, inPlace =False):
        """ Iterates through the elements of the target list and converts each of them to unicode
            strings, including decoding byte strings to unicode strings."""

        from pyaid.string.StringUtils import StringUtils

        output = target if inPlace else []
        index  = 0

        while index < len(target):
            source = target[index]
            if StringUtils.isStringType(source):
                output[index] = StringUtils.strToUnicode(source)
            else:
                output[index] = StringUtils.toUnicode(source)

        return output

#___________________________________________________________________________________________________ hasAny
    @classmethod
    def hasAny(cls, target, options):
        """ Returns true if any of the options are found within the target list or tuple, otherwise
            returns False. """
        if not options:
            return False

        for item in options:
            if item in target:
                return True
        return False

#___________________________________________________________________________________________________ indexOfAny
    @classmethod
    def indexOfAny(cls, target, options):
        """ Finds any of the iterable options in the target list or tuple and returns the index if
            found or -1 otherwise. """
        if not options:
            return -1

        for item in options:
            try:
                index = target.find(item)
            except Exception:
                continue
            return index

        return -1

#___________________________________________________________________________________________________ listToRanges
    @classmethod
    def listToRanges(cls, source):
        """ Takes a list of integers and turns it into a list tuples representing continous ranges. """
        if not source:
            return []

        source = sorted(list(set(source)))
        start  = source[0]
        last   = start
        out    = []
        for entry in source[1:]:
            if entry == last + 1:
                last = entry
                continue

            out.append((start, last + 1))
            start = entry
            last  = entry

        out.append((start, last + 1))
        return out

#___________________________________________________________________________________________________ addIfMissing
    @classmethod
    def addIfMissing(cls, value, targetList, reorder =False, frontOrdering =False):
        """ Adds the specified value to the target list if and only if the value is not already in
            the target list.

            @@@param value:*
                The value you want added to the list if it is not in the list already.

            @@@param targetList:list
                The list on which you want the value added.

            @@@param reorder:bool
                If True the order of the list will change so that the value appears at the end of
                the list. If the value wasn't there all ready it will be added. If the value was
                in the list it will be moved to the end.

            @@@param frontOrdering:bool
                If True, the value will be added at the beginning of the list instead of the end.
                This is true if reordering is used as well.

            @@@return bool
                Whether or not the value was added to the list (ignores reordering).
        """

        if not targetList:
            targetList.append(value)
            return True

        if value not in targetList:
            if frontOrdering:
                targetList.insert(0, value)
            else:
                targetList.append(value)
            return True

        if not reorder:
            return False

        targetList.remove(value)
        if frontOrdering:
            targetList.insert(0, value)
        else:
            targetList.append(value)

        return False

#___________________________________________________________________________________________________ clone
    @classmethod
    def clone(cls, item):
        out = []
        for value in item:
            if isinstance(value, dict):
                from pyaid.dict.DictUtils import DictUtils
                out.append(DictUtils.clone(value))
            elif isinstance(value, list) or isinstance(value, tuple):
                out.append(ListUtils.clone(value))
            else:
                out.append(value)

        if isinstance(item, tuple):
            return tuple(out)
        return out

#___________________________________________________________________________________________________ getAbsoluteIndex
    @staticmethod
    def getAbsoluteIndex(index, target):
        l = len(target)
        return (l - (-1*index % l)) % l

#___________________________________________________________________________________________________ contains
    @staticmethod
    def contains(source, search):

        from pyaid.string.StringUtils import StringUtils
        if StringUtils.isStringType(search):
            return search in source

        for s in search:
            if s in source:
                return True

        return False

#___________________________________________________________________________________________________ sortListByIndex
    @classmethod
    def sortListByIndex(cls, source, index, inPlace =False, reversed =False):
        """ Sorts a list of lists and/or tuples by the specified index. """
        if inPlace:
            source.sort(key=lambda x:x[index], reverse=reversed)
            return source
        return sorted(source, key=lambda x:x[index], reverse=reversed)

#___________________________________________________________________________________________________ sortDictionaryList
    @classmethod
    def sortDictionaryList(cls, source, key, inPlace =False, reversed =False):
        """Sorts a list of dictionaries by the specified key."""
        if inPlace:
            source.sort(key=itemgetter(key), reverse=reversed)
            return source
        return sorted(source, key=itemgetter(key), reverse=reversed)

#___________________________________________________________________________________________________ sortObjectList
    @classmethod
    def sortObjectList(src, source, property, inPlace = False, reversed =False):
        """ Sorts the specified source list of object instances (i.e. new type class instances) by
            the specified property and returns the sorted source list.
        """
        if inPlace:
            source.sort(key=attrgetter(property), reverse=reversed)
            return source

        return sorted(source, key=attrgetter(property), reverse=reversed)

#___________________________________________________________________________________________________ compare
    @classmethod
    def compare(cls, a, b):
        if a == b:
            return True

        if a is None or b is None:
            return False

        if len(a) != len(b):
            return False

        for i in range(len(a)):
            # Compare dict values
            if isinstance(a[i], dict) and isinstance(b[i], dict):
                from pyaid.dict.DictUtils import DictUtils
                if not DictUtils.compare(a[i], b[i]):
                    return False

            # Compare list values
            if isinstance(a[i], list) or isinstance(a[i], tuple):
                if not cls.compare(a[i], b[i]):
                    return False

            if a[i] != b[i]:
                return False
