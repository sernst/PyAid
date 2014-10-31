# SystemSocketDaemon.py
# (C)2012-2014
# Scott Ernst

import os
import SocketServer

from pyaid.system.service.systemd.SystemDaemon import SystemDaemon
from pyaid.debug.Logger import Logger

#___________________________________________________________________________________________________ SystemSocketDaemon
class SystemSocketDaemon(SystemDaemon):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    SERVICE_UID   = 'testsocket'
    WAIT_INTERVAL = 10
    VERBOSE       = False
    SOCKET_ROOT_PATH = '/var/run/'

#___________________________________________________________________________________________________ __init__
    def __init__(self, contextRunner, socketHandler):
        """Creates a new instance of SystemSocketDaemon.

        @@@param contextRunner:DaemonRunner
            The running context that wraps this execution within a systemd service or orphan daemon.
        """
        SystemDaemon.__init__(self, contextRunner, Logger(socketHandler.__name__))

        self._server        = None
        self._socketHandler = socketHandler
        self._socket        = os.path.join(self.SOCKET_ROOT_PATH, contextRunner.uid + '.sock')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: verbose
    @property
    def verbose(self):
        return getattr(self._socketHandler, 'VERBOSE', False)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ __call__
    def __call__(self):
        """The callable action for the SystemSocketDaemon, which executes the _run method within the
        context of a systemd service.

        @@@return boolean
            Specifies whether or not to continue execution of the daemon after this returns. True
            equates to a continue, False will break execution and disable the daemon.
        """

        if self.verbose:
            self.logger.write('Cleaning up leftover socket file')
        try:
            os.unlink(self._socket)
        except Exception, err:
            pass

        if self.verbose:
            self.logger.write('Creating socket server')
        self._server = SocketServer.UnixStreamServer(self._socket, self._socketHandler)

        if self.verbose:
            self.logger.write('Executing socket server polling')
        try:
            self._server.serve_forever()
        except Exception, err:
            self.logger.write('FAILED: serve_forever', err)

        if self.verbose:
            self.logger.write('Closed socket server polling')

        return False

#___________________________________________________________________________________________________ cleanup
    def cleanup(self):
        try:
            os.unlink(self._socket)
        except Exception, err:
            pass

#___________________________________________________________________________________________________ terminate
    def terminate(self):
        if self._terminated:
            return

        self._terminated = True

        try:
            self._server.shutdown()
        except Exception, err:
            pass

        self.cleanup()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s | %s | %s>' % (
            self.__class__.__name__,
            self._socketHandler.__name__,
            self._socket)
