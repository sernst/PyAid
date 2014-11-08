# TestDaemon.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.system.service.systemd.SystemDaemon import SystemDaemon

#___________________________________________________________________________________________________ TestDaemon
class TestDaemon(SystemDaemon):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    SERVICE_UID   = 'helloPyAidWorld'
    WAIT_INTERVAL = 10
    VERBOSE       = True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _run
    def _run(self, **kwargs):
        """ Execution command that should be overridden in subclasses.

            return |boolean
                True if the daemon should continue execution upon return of this method or False
                if the daemon and service should be aborted. """

        self.logger.write('Hello from this serviced daemon test :)')

        return True

