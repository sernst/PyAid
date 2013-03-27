# HashUtils.py
# (C)2012
# Eric D. Wills and Scott Ernst

import base64
import hashlib
import hmac

# AS NEEDED: from pyaid.json.JSON import JSON

#___________________________________________________________________________________________________ HashUtils
class HashUtils(object):
    """Utility class for hash operations."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ base64Encode
    @staticmethod
    def base64Encode(text):
        return base64.b64encode(text, '-~').replace('=', '_')

#___________________________________________________________________________________________________ sha256hmac
    @staticmethod
    def sha256hmac(key, text):
        """Returns a HMAC-SHA256 hex hash of the specified text based on the specified key."""

        msg  = HashUtils.base64Encode(text.encode('utf8', 'ignore'))
        hash = hmac.new(str(key), msg=msg, digestmod=hashlib.sha256).digest()
        return HashUtils.base64Encode(hash)

#___________________________________________________________________________________________________ sha256hmacSign

    @staticmethod
    def sha256hmacSign(key, **kwargs):
        from pyaid.json.JSON import JSON

        return HashUtils.sha256hmac(key, JSON.asString(kwargs))

#___________________________________________________________________________________________________ sha256hmacSignObject
    @staticmethod
    def sha256hmacSignObject(key, obj):
        from pyaid.json.JSON import JSON

        return HashUtils.sha256hmac(key, JSON.asString(obj))
