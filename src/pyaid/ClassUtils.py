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

#___________________________________________________________________________________________________ dynamicImport
    @classmethod
    def dynamicImport(cls, package, target =None):
        if isinstance(target, basestring):
            singular = True
            target   = [target]
        elif not target:
            target   = [package.split(u'.')[-1]]
            singular = True
        else:
            singular = False

        result = __import__(package, globals(), locals(), target)
        if singular:
            return getattr(result, target[0], None)
        return result
