# ClassGetter.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ ClassGetter
class ClassGetter(object):
    """A decorator which allows definition of a Python descriptor with class-level behavior."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, fget):
        """Create a new ClassGetter"""
        self.fget = fget

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ __get__
    def __get__(self, instance, owner):
        return self.fget(owner)

