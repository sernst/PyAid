# EmailUtils.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

#___________________________________________________________________________________________________ EmailUtils
class EmailUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    #-----------------------------------------------------------------------------------------------
    # 3.2.1
    NO_WS_CTL       = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'

    #-----------------------------------------------------------------------------------------------
    # 3.2.2
    QUOTED_PAIR     = r'(?:\\.)'

    #-----------------------------------------------------------------------------------------------
    # 3.2.3
    FWS             = r'(?:(?:[ \t]*[ \t])?%s+)'
    C_TEXT          = r'[%s\x21-\x27\x2a-\x5b\x5d-\x7e]' % NO_WS_CTL
    C_CONTENT       = r'(?:%s|%s)' % (C_TEXT, QUOTED_PAIR)
    COMMENT         = r'\((?:%s?%s)*%s?\)' % (FWS, C_CONTENT, FWS)
    CFWS            = r'(?:%s?%s)*(?:%s?%s|%s)' % (FWS, COMMENT, FWS, COMMENT, FWS)

    #-----------------------------------------------------------------------------------------------
    # 3.2.4
    A_TEXT          = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'
    ATOM            = r'%s?%s+%s?' % (CFWS, A_TEXT, CFWS)
    DOT_ATOM_TEXT   = r'%s+(?:\.%s+)*' % (A_TEXT, A_TEXT)
    DOT_ATOM        = r'%s?%s?' % (CFWS, DOT_ATOM_TEXT + CFWS)

    #-----------------------------------------------------------------------------------------------
    # 3.2.5
    Q_TEXT          = r'[%s\x21\x23-\x5b\x5d-\x7e]' % NO_WS_CTL
    Q_CONTENT       = r'(?:%s|%s)' % (Q_TEXT, QUOTED_PAIR)
    QUOTED_STRING   = r'%s?"(?:%s?%s)*%s?"%s?' % (CFWS, FWS, Q_CONTENT, FWS, CFWS)

    #-----------------------------------------------------------------------------------------------
    # 3.4.1
    LOCAL_PART      = r'(?:%s|%s)' % (DOT_ATOM, QUOTED_STRING)
    D_TEXT          = r'[%s\x21-\x5a\x5e-\x7e]' % NO_WS_CTL
    D_CONTENT       = r'(?:%s|%s)' % (D_TEXT, QUOTED_PAIR)
    DOMAIN_LITERAL  = r'%s?\[(?:%s?%s)*%s?\]%s?' % (CFWS, FWS, D_CONTENT, FWS, CFWS)
    DOMAIN          = r'(?:%s|%s)' % (DOT_ATOM, DOMAIN_LITERAL)

    VALID_ADDRESS   = r'%s@%s' % (LOCAL_PART, DOMAIN)
    ADDRESS_MATCH   = r'^%s$' % VALID_ADDRESS

#___________________________________________________________________________________________________ validate
    @classmethod
    def validate(cls, address):
        """ Checks the specified email address against the ADDRESS_MATCH regular expression and
            returns True if the address conforms to the specified email address. """
        return re.match(cls.ADDRESS_MATCH, address) is not None
