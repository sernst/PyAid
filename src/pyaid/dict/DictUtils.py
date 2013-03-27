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
        if vi[1] < 7 and vi[0] < 3:
            out = dict()
            for n,v in source.iteritems():
                out[str(n)] = v
        else:
            out = source

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

