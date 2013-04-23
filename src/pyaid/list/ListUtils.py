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
