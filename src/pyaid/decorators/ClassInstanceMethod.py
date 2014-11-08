# ClassInstanceMethod.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#################################################################################################### ClassInstanceMethod
class ClassInstanceMethod(object):
    """ A method that behaves as both a class method when called from a class and as an instance
        method when called by an instance. The method being decorated must take two arguments,
        'self' and 'cls'; one of these will be None depending on how the method was called.
    """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, func):
        self.func = func

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ __get__
    def __get__(self, obj, type=None):
        return _MethodWrapper(self.func, obj=obj, type=type)

#################################################################################################### _MethodWrapper
class _MethodWrapper(object):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ __call__
    def __call__(self, *args, **kwargs):
        assert 'self' not in kwargs and 'cls' not in kwargs, (
            "You cannot use 'self' or 'cls' arguments to a ClassInstanceMethod")
        try:
            return self.func(self.obj, self.type, *args, **kwargs)
        except Exception:
            print('ClassInstanceMethod execution failure:')
            print('\tOBJECT:', self.obj)
            print('\tTYPE:', self.type)
            print('\tARGS:', args)
            print('\tKWARGS:', kwargs)
            raise

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        if self.obj is None:
            out = '<bound class method %s.%s>' % (self.type.__name__, self.func.func_name)
        else:
            out = '<bound method %s.%s of %r>' % (self.type.__name__, self.func.func_name, self.obj)
        return out
