# ListUtils.py
# (C)2011-2013
# Scott Ernst

from operator import itemgetter
from operator import attrgetter

# AS NEEDED: from pyaid.dict.DictUtils import DictUtils

#___________________________________________________________________________________________________ ListUtils
class ListUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

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

        if isinstance(search, basestring):
            return search in source

        for s in search:
            if s in source:
                return True

        return False

#___________________________________________________________________________________________________ sortDictionaryList
    @staticmethod
    def sortDictionaryList(source, key):
        """Sorts a list of dictionaries by the specified key."""

        return sorted(source, key=itemgetter(key))

#___________________________________________________________________________________________________ sortObjectList
    @staticmethod
    def sortObjectList(source, prop):
        """ Sorts the specified source list of object instances (i.e. new type class instances) by
            the specified property and returns the sorted source list.
        """

        source.sort(key = attrgetter(prop))
        return source

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
