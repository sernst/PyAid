# NullUtils.py
# (C)2011-2012
# Scott Ernst

from collections import namedtuple

NULL_CLASS_NT = namedtuple('NULL_CLASS_NT', ['id'])

#___________________________________________________________________________________________________ NullUtils
class NullUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

    NULL           = NULL_CLASS_NT

    UNIVERSAL_NULL = NULL_CLASS_NT('GLOBAL_NULL')
