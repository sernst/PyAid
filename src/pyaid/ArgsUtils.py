# ArgsUtils.py
# (C)2011-2013
# Scott Ernst

# AS NEEDED: from pyaid.debug.Logger import Logger

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ ArgsUtils
class ArgsUtils(object):

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ addIfMissing
    @staticmethod
    def addIfMissing(name, value, kwargs, overwriteNone =False):
        """Adds the value to the kwargs dictionary if the key does not exist."""

        if kwargs.has_key(name) and not (overwriteNone and kwargs.get(name) is None):
            return False

        kwargs[name] = value
        return True

#___________________________________________________________________________________________________ get
    @staticmethod
    def get(name, defaultValue =None, kwargs =None, args =None, index =None, allowNone =True):
        if args and not index is None and (index < 0 or index < len(args)):
            out = args[index]
            if not allowNone and args[index] is None:
                return defaultValue
            return out

        try:
            if StringUtils.isStringType(name):
                if name in kwargs:
                    out = kwargs[name]
                    if not allowNone and out is None:
                        return defaultValue
                    return out
            else:
                for n in name:
                    if n in kwargs:
                        out = kwargs[n]
                        if not allowNone and out is None:
                            return defaultValue
                        return out
        except Exception as err:
            pass

        return defaultValue

#___________________________________________________________________________________________________ getAs
    @staticmethod
    def getAs(name, defaultValue =None, kwargs =None, args =None, index =None, asClass =None):
        res = ArgsUtils.get(name, None, kwargs, args, index)
        if res is None:
            if asClass:
                if isinstance(defaultValue, asClass):
                    return defaultValue
                else:
                    if defaultValue is None:
                        return None
                    else:
                        return asClass(defaultValue)
            return defaultValue

        if not isinstance(res, asClass):
            return asClass(res)

        return res

#___________________________________________________________________________________________________ getAsList
    @staticmethod
    def getAsList(name, kwargs =None, args =None, index =None, defaultValue =None):
        res = ArgsUtils.get(name, None, kwargs, args, index)
        if res is None:
            return defaultValue if defaultValue else []

        if not isinstance(res, list):
            return [res]

        return res

#___________________________________________________________________________________________________ getAsDict
    @staticmethod
    def getAsDict(name, kwargs =None, args =None, index =None, defaultValue =None):
        res = ArgsUtils.get(name, None, kwargs, args, index)
        if res is None:
            return defaultValue if defaultValue else dict()
        return res

#___________________________________________________________________________________________________ getLogger
    @staticmethod
    def getLogger(
            logIdentifier, kwargs =None, args =None, index =None, name ='logger', extract =False,
            trace =None
    ):
        if extract:
            res = ArgsUtils.extract(name, None, kwargs, args, index)
        else:
            res = ArgsUtils.get(name, None, kwargs, args, index)

        if res is None:
            from pyaid.debug.Logger import Logger
            res = Logger(logIdentifier)

        if trace is not None:
            res.trace = trace

        return res

#___________________________________________________________________________________________________ extract
    @staticmethod
    def extract(name, defaultValue, kwargs, args =None, index =None):
        """ Returns the value if one was specified and if the argument was in the kwargs dictionary
            deletes it.
        """
        value = ArgsUtils.get(name, defaultValue, kwargs, args, index)
        if name in kwargs:
            del(kwargs[name])
        return value
