# Reflection.py
# (C)2011-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ Reflection
class Reflection(object):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getEnumerationReflectionDict
    @classmethod
    def getEnumerationReflectionDict(cls, source):
        """ Creates a dictionary from a multi-value enumeration class in the format:
            (enumerationValue, (possible, matching, values))
        """
        res = dict()

        for attr in dir(source):
            if attr.startswith('_'):
                continue

            a = getattr(source, attr)
            for enum in a[1]:
                res[enum] = a[0]

        return res

#___________________________________________________________________________________________________ getReflectionDict
    @staticmethod
    def getReflectionDict(source, lowerKeys =False, includeProtected =False, includeIntrinsic =False):
        """ Uses reflection to get the attributes of source and returns the results as a dictionary
            with the keys being the names of the source attributes. Attributes that begin with an
            underscore are considered private and ignored.
        """

        res = dict()

        for attr in dir(source):
            if attr[0] == '_':
                if not includeProtected:
                    continue

                if not includeIntrinsic and attr[1] == '_':
                    continue

            a = getattr(source, attr)
            if not a:
                continue

            if lowerKeys:
                res[attr.lower()] = a
            else:
                res[attr] = a

        return res

#___________________________________________________________________________________________________ getReflectionList
    @staticmethod
    def getReflectionList(source):
        """ Uses reflection to get the attribute values of source and returns those as a list.
            Attributes that begin with an underscore are considered private and ignored.
        """

        res = []

        for attr in dir(source):
            if attr.startswith('_'):
                continue

            a = getattr(source, attr)
            if not a:
                continue

            res.append(a)

        return res


#___________________________________________________________________________________________________ getReflectionAttributeList
    @staticmethod
    def getReflectionAttributeList(source):
        """ Uses reflection to get the attribute names of source and returns those as a list.
            Attributes that begin with an underscore are considered private and ignored.
        """

        res = []

        for attr in dir(source):
            if attr.startswith('_'):
                continue

            a = getattr(source, attr)
            if not a:
                continue

            res.append(attr)

        return res

#___________________________________________________________________________________________________ getReflectionNameValueLists
    @staticmethod
    def getReflectionNameValueLists(source):
        """ Uses reflection to get the attribute name and value lists of source and returns those as
            two lists. Attributes that begin with an underscore are considered private and ignored.
        """

        names  = []
        values = []

        for attr in dir(source):
            if attr.startswith('_'):
                continue

            a = getattr(source, attr)
            if not a:
                continue

            names.append(attr)
            values.append(a)

        return names, values
