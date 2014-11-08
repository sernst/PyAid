# ServiceUtils.py
# (C)2012
# Scott Ernst

import re
import subprocess

#___________________________________________________________________________________________________ ServiceUtils
class ServiceUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

    ACTIVE_STATE    = 'active'
    INACTIVE_STATE  = 'inactive'
    FAILED_STATE    = 'failed'
    UNKNOWN_STATE   = 'unknown'

    _STATE_REGEX    = re.compile('Active: (?P<state>[^\s]+)\s')

#___________________________________________________________________________________________________ getState
    @classmethod
    def getState(cls, serviceUID):
        if not serviceUID.endswith('.service'):
            serviceUID += '.service'

        try:
            out = subprocess.check_output(['systemctl', 'status', serviceUID])
        except Exception:
            return cls.INACTIVE_STATE

        res = cls._STATE_REGEX.search(out)
        if not res:
            return cls.UNKNOWN_STATE

        result = res.group('state').lower()
        if result == 'active':
            return cls.ACTIVE_STATE
        elif result == 'failed':
            return cls.FAILED_STATE

        return cls.INACTIVE_STATE

#___________________________________________________________________________________________________ reload
    @classmethod
    def reload(cls, serviceUID):
        if not serviceUID.endswith('.service'):
            serviceUID += '.service'

        status = subprocess.check_call(['systemctl', 'restart', serviceUID])
        if status:
            return False

        return True
