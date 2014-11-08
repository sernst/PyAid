# TestSocketHandler.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.system.service.systemd.SocketHandler import SocketHandler

#___________________________________________________________________________________________________ TestSocketHandler
class TestSocketHandler(SocketHandler):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    SERVICE_UID   = 'helloPyAidSocket'
    VERBOSE       = True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _respondImpl
    def _respondImpl(self, data):
        self.logger.write('RESPONDING TO: ' + str(data))
