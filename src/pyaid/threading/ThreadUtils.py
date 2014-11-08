# ThreadUtils.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import threading

from pyaid.radix.Base64 import Base64

#___________________________________________________________________________________________________ ThreadUtils
class ThreadUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getCurrentID
    @classmethod
    def getCurrentID(cls, sep ='::'):
        return str(os.getpid()) + '-' + Base64.to64(threading.current_thread().ident) \
            + sep + str(threading.current_thread().name)
