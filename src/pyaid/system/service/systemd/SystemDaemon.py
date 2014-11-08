# SystemDaemon.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.debug.Logger import Logger

#___________________________________________________________________________________________________ SystemDaemon
class SystemDaemon(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    SERVICE_UID   = 'test'
    WAIT_INTERVAL = 10
    VERBOSE       = False
    WORK_PATH     = '/var/lib/'
    RUN_PATH      = '/var/run/'
    LOG_PATH      = '/var/log/'

#___________________________________________________________________________________________________ __init__
    def __init__(self, contextRunner, logger =None, **kwargs):
        """ Creates a new instance of SystemDaemon.

            contextRunner |DaemonRunner
                The running context that wraps this execution within a systemd service or orphan
                daemon. """

        self._contextRunner = contextRunner
        self._logger        = logger if logger else self.getLogger()
        self._terminated    = False

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: logger
    @property
    def logger(self):
        return self._logger

#___________________________________________________________________________________________________ GS: verbose
    @property
    def verbose(self):
        return getattr(self.__class__, 'VERBOSE', False)

#___________________________________________________________________________________________________ GS: terminated
    @property
    def terminated(self):
        return self._terminated

#___________________________________________________________________________________________________ GS: blocking
    @property
    def blocking(self):
        return not getattr(self.__class__, 'NON_BLOCKING', False)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ cleanup
    def cleanup(self):
        pass

#___________________________________________________________________________________________________ terminate
    def terminate(self):
        self._terminated = True

#___________________________________________________________________________________________________ __call__
    def __call__(self):
        """The callable action for the SystemDaemon, which executes the _run method within the
        context of a systemd service.

        @@@return boolean
            Specifies whether or not to continue execution of the daemon after this returns. True
            equates to a continue, False will break execution and disable the daemon.
        """

        return self._run()

#___________________________________________________________________________________________________ getLogger
    @classmethod
    def getLogger(cls):
        """getLogger doc..."""
        return Logger(cls, printOut=False, logFolder=cls.LOG_PATH)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _run
    def _run(self, **kwargs):
        """Execution command that should be overridden in subclasses.

        @@@return boolean
            True if the daemon should continue execution upon return of this method or False if the
            daemon and service should be aborted.
        """

        return True
