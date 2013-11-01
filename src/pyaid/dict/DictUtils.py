# DictUtils.py
# (C)2012-2013
# Scott Ernst

import sys

# AS NEEDED: from pyaid.list.ListUtils import ListUtils

#___________________________________________________________________________________________________ DictUtils
class DictUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ merge
    @classmethod
    def merge(cls, a, b):
        if a and not b:
            return a
        elif b and not a:
            return b
        elif not a and not b:
            return None

        keys = tuple(set(a.keys() + b.keys()))
        out  = dict()
        for k in keys:
            if k not in b:
                out[k] = a[k]
                continue
            if k not in a:
                out[k] = b[k]
                continue
            out[k] = cls._mergeValues(a[k], b[k])

        return out

#___________________________________________________________________________________________________ clone
    @classmethod
    def clone(cls, item):
        out = dict()
        for key, value in item.iteritems():
            if isinstance(value, dict):
                # Clone dict recursively
                out[key] = cls.clone(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                # Clone lists and tuples
                from pyaid.list.ListUtils import ListUtils
                out[key] = ListUtils.clone(value)
            else:
                out[key] = value

        return out

#___________________________________________________________________________________________________ cleanDictKeys
    @classmethod
    def cleanDictKeys(cls, source):
        """ Python 2.6 and below don't allow unicode argument keys, so these must be converted to
            byte strings explicitly to prevent exceptions.
        """

        vi = sys.version_info
        if vi[0] == 2 and (vi[1] < 7 or vi[0] < 5):
            out = dict()
            for n,v in source.iteritems():
                out[str(n)] = v
        else:
            out = source

        return out

#___________________________________________________________________________________________________ lowerDictKeys
    @classmethod
    def lowerDictKeys(cls, source):
        out = dict()
        for key, value in source.iteritems():
            out[key.lower()] = value
        return out

#___________________________________________________________________________________________________ compare
    @classmethod
    def compare(cls, a, b):
        if a == b:
            return True

        if a is None or b is None:
            return False

        if len(a.keys()) != len(b.keys()):
            return False

        for name, value in a.iteritems():
            if name not in b:
                return False

            # Compare dict values
            if isinstance(value, dict):
                if isinstance(b[name], dict):
                    if not cls.compare(value, b[name]):
                        return False

            # Compare list and tuples
            if isinstance(value, list) or isinstance(value, tuple):
                from pyaid.list.ListUtils import ListUtils
                if not ListUtils.compare(value, b[name]):
                    return False

            if value != b[name]:
                return False

        return True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _mergeValues
    @classmethod
    def _mergeValues(cls, a, b):
        if a and not b:
            return a
        elif b and not a:
            return b

        if isinstance(a, list):
            if isinstance(b, list):
                return a + b
            return a + [b]
        elif isinstance(a, tuple):
            if isinstance(b, tuple):
                return a + b
            return a + (b,)
        elif isinstance(b, list):
            return [a] + b
        elif isinstance(b, tuple):
            return (a,) + b
        elif isinstance(a, dict):
            if isinstance(b, dict):
                return cls.merge(a, b)
            return a

        return b
