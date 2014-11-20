# ConfigsDict.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
from pyaid.NullUtils import NullUtils
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ ConfigsDict
class ConfigsDict(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NULL = NullUtils.NULL('ConfigsDict')

#___________________________________________________________________________________________________ __init__
    def __init__(self, data =None, *args, **kwargs):
        """Creates a new instance of ConfigsDict."""
        self.isCaseSensitive = ArgsUtils.get('isCaseSensitive', False, kwargs)
        self._data = data if data else dict()
        self._null = ArgsUtils.get('null', self.NULL, kwargs, args, 0)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: data
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value
        if self._data is None:
            self._data = dict()

#___________________________________________________________________________________________________ GS: null
    @property
    def null(self):
        return self._null
    @null.setter
    def null(self, value):
        self._null = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ load
    def load(self, data):
        """load doc..."""
        self._data = data if data else dict()

#___________________________________________________________________________________________________ unload
    def unload(self):
        """unload doc..."""
        self.load(None)

#___________________________________________________________________________________________________ add
    def add(self, key, value, defaultValue =None):
        return self.set(key, value, defaultValue=defaultValue)

#___________________________________________________________________________________________________ set
    def set(self, key, value, defaultValue =None):
        if not key:
            return False

        if value is None or value == defaultValue:
            self.remove(key)
            return True

        if not StringUtils.isStringType(key) and len(key) == 1:
            key = key[0]

        if StringUtils.isStringType(key):
            addKey = self._formatKey(key)
            source = self._data
        else:
            addKey = self._formatKey(key[-1])
            source = self._data
            temp   = self._data
            for k in key[:-1]:
                temp = self._getFrom(temp, k)
                if temp == self.null:
                    temp = dict()
                    source[self._formatKey(k)] = temp
                source = temp

        source[addKey] = value
        return True

#___________________________________________________________________________________________________ remove
    def remove(self, key):
        if not key:
            return False

        if not StringUtils.isStringType(key) and len(key) == 1:
            key = key[0]

        if StringUtils.isStringType(key):
            k, value  = self._getFrom(self._data, key, includeKey=True)
            if value == self.null:
                return False
            hierarchy = [(k, self._data)]
        else:
            value, hierarchy = self.get(key, defaultValue=self.null, includeHierarchy=True)
            if value == self.null or not hierarchy:
                return False

        while len(hierarchy) > 0:
            item = hierarchy.pop()
            del item[1][item[0]]
            if item[1]:
                return True
        return True

#___________________________________________________________________________________________________ has
    def has(self, key, allowFalse =True):
        out     = self.get(key, self.null)
        result  = out != self.null
        if allowFalse:
            return result
        return out and result

#___________________________________________________________________________________________________ get
    def get(self, key, defaultValue =None, includeHierarchy =False):
        if not key:
            return (defaultValue, None) if includeHierarchy else defaultValue

        hierarchy = []
        if StringUtils.isStringType(key):
            key, value = self._getFrom(self._data, key, includeKey=True)
            if value == self.null:
                return (defaultValue, None) if includeHierarchy else defaultValue
            hierarchy.append((key, self._data))
            return (value, hierarchy) if includeHierarchy else value

        source = self._data
        for k in key:
            sourceKey, value = self._getFrom(source, k, includeKey=True)
            if value == self.null:
                return (defaultValue, None) if includeHierarchy else defaultValue
            hierarchy.append((sourceKey, source))
            source = value

        return (source, hierarchy) if includeHierarchy else source

#___________________________________________________________________________________________________ swap
    def swap(self, key, value, defaultValue =None, includeHierarchy =False):
        """ Swaps the currently stored value with the new specified value and returns the old
            value, allowing you to get and set in a single operation. """
        out = self.get(key, defaultValue=defaultValue, includeHierarchy=includeHierarchy)
        self.set(key, value, defaultValue=defaultValue)
        return out

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _formatKey
    def _formatKey(self, key):
        """_formatKey doc..."""
        return key if self.isCaseSensitive else key.lower()

#___________________________________________________________________________________________________ _getFrom
    def _getFrom(self, source, key, includeKey =False):
        if key in source:
            return (key, source[key]) if includeKey else source[key]

        if self.isCaseSensitive:
            return (key, self.null) if includeKey else self.null

        key = self._formatKey(key)
        for value in source.items():
            if self._formatKey(value[0]) == key:
                return value if includeKey else value[1]
        return (key, self.null) if includeKey else self.null

#___________________________________________________________________________________________________ __testing__
    @classmethod
    def __testing__(cls):
        """ Unit testing method to verify that the basic behaviors are working correctly """
        keyBase = ['abC', 'deF', 'ghI', 'jkL', 'ZeRo']
        keys = [
            keyBase,
            'ONE',
            [keyBase[0], 'TWO'],
            keyBase[:-3] + ['THREE'] ]

        trials = [
            ('CASE SENSITIVE:', True),
            ('CASE INSENSITIVE:', False) ]

        for trial in trials:
            print('\n' + 80*'-' + '\n' + trial[0])
            cd = ConfigsDict(isCaseSensitive=trial[1])
            print('START:\n', cd.data)
            cd.add(keys[0], 42)
            print('ADDED KEY:\n', keys[0], '\n', cd.data)
            cd.remove(keys[0])
            print('REMOVED KEY:\n', keys[0], '\n', cd.data)

            for key in keys:
                cd.add(key, 'KEY-' + str(keys.index(key)))
                value = cd.get(key)
                print('ADDED KEY:\n', '%s -> %s' % (key, value), '\n', cd.data)

            for key in keys:
                cd.remove(key)
                value = cd.get(key)
                print('REMOVED KEY:\n', '%s -> %s' % (key, value), '\n', cd.data)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

