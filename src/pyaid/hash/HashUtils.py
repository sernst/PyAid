# HashUtils.py
# (C)2012-2014
# Eric D. Wills and Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import base64
import hashlib
import hmac

from pyaid.json.JSON import JSON
from pyaid.string.StringUtils import StringUtils


#___________________________________________________________________________________________________ HashUtils
class HashUtils(object):
    """Utility class for hash operations."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ base64Encode
    @staticmethod
    def base64Encode(text):
        b = StringUtils.toBytes
        return base64.b64encode(b(text), b('-~')).replace(b('='), b('_'))

#___________________________________________________________________________________________________ sha256hmac
    @classmethod
    def sha256hmac(cls, key, text):
        """Returns a HMAC-SHA256 hex hash of the specified text based on the specified key."""

        msg  = cls.base64Encode(text)
        hash = hmac.new(StringUtils.toBytes(key), msg=msg, digestmod=hashlib.sha256).digest()
        return cls.base64Encode(hash)

#___________________________________________________________________________________________________ sha256hmacSign
    @classmethod
    def sha256hmacSign(cls, key, **kwargs):
        return cls.sha256hmac(key, JSON.asString(kwargs))

#___________________________________________________________________________________________________ sha256hmacSignObject
    @classmethod
    def sha256hmacSignObject(cls, key, obj):
        return cls.sha256hmac(key, JSON.asString(obj))
