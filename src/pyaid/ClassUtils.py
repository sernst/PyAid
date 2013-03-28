# ClassUtils.py
# (C)2012-2013
# Scott Ernst

import inspect

#___________________________________________________________________________________________________ ClassUtils
class ClassUtils(object):

#===================================================================================================
#                                                                                       C L A S S


#___________________________________________________________________________________________________ getAttrFromClass
    @classmethod
    def getAttrFromClass(cls, targetClass, attr, defaultValue =None):
        """Search through class and its parent classes if necessary to find the attr value."""

        if not inspect.isclass(targetClass):
            targetClass = targetClass.__class__

        out = defaultValue
        if hasattr(targetClass, attr):
            out = getattr(targetClass, attr, defaultValue)
        else:
            bases = inspect.getmro(cls)
            for b in bases:
                if hasattr(b, attr):
                    out = getattr(b, attr, defaultValue)
                    break

        return out
