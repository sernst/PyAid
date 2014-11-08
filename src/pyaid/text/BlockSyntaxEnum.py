# BlockSyntaxEnum.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ BlockSyntaxEnum
class BlockSyntaxEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    COMMENT = 'comment'

    STRING = 'string'

    REGEX = 'regex'

    PARENS = 'parens'

    BRACES = 'braces'

    BRACKETS = 'brackets'

    LIST_ITEM = 'list_item'

    VIZMEML_OPEN  = 'vizmeml_open'

    VIZMEML_CLOSE = 'vizmeml_close'

    VIZMEML_ATTR = 'vizmeml_attr'

    DOC_TAG = 'doc_tag'
