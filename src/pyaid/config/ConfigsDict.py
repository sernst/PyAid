# ConfigsDict.py
# (C)2013
# Scott Ernst

from pyaid.ArgsUtils import ArgsUtils
from pyaid.NullUtils import NullUtils

#___________________________________________________________________________________________________ ConfigsDict
class ConfigsDict(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NULL = NullUtils.NULL('ConfigsDict')

#___________________________________________________________________________________________________ __init__
    def __init__(self, data =None, *args, **kwargs):
        """Creates a new instance of ConfigsDict."""
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

#___________________________________________________________________________________________________ add
    def add(self, key, value):
        if not key:
            return False

        if not isinstance(key, basestring) and len(key) == 1:
            key = key[0]

        if isinstance(key, basestring):
            addKey = key.lower()
            source = self._data
        else:
            addKey = key[-1].lower()
            source = self._data
            temp   = self._data
            for k in key[:-1]:
                temp = self._getFromDataDict(k.lower(), temp)
                if temp == self.null:
                    temp = dict()
                    source[k.lower()] = temp
                source = temp

        source[addKey] = value
        return True

#___________________________________________________________________________________________________ remove
    def remove(self, key):
        if not key:
            return False

        if not isinstance(key, basestring) and len(key) == 1:
            key = key[0]

        if not isinstance(key, basestring):
            removeKey = key[-1].lower()
            source    = self.get(key[:-1])
            if not source:
                return False
        else:
            source    = self._data
            removeKey = key.lower()

        for item in source.items():
            if removeKey == item[0].lower():
                del source[item[0]]
                return True
        return False

#___________________________________________________________________________________________________ has
    def has(self, key, allowFalse =True):
        out     = self.get(key, self.null)
        result  = out != self.null
        if allowFalse:
            return result
        return out and result

#___________________________________________________________________________________________________ get
    def get(self, key, defaultValue =None):
        if not key:
            return defaultValue

        if not isinstance(key, basestring):
            source = self._data
            for k in key:
                source = self._getFromDataDict(k.lower(), source)
                if source == self.null:
                    return defaultValue
            return source

        out = self._getFromDataDict(key.lower(), self._data)
        if out == self.null:
            return defaultValue
        return out

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getFromDataDict
    def _getFromDataDict(self, key, source):
        for value in source.items():
            if value[0].lower() == key:
                return value[1]
        return self.null

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

