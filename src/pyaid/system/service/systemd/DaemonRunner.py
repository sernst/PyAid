# DaemonRunner.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import sys
import signal
import time

import lockfile
import daemon

from pyaid.ArgsUtils import ArgsUtils

#AS NEEDED: from pyaid.system.service.systemd.SystemSocketDaemon import SystemSocketDaemon

#___________________________________________________________________________________________________ DaemonRunner
class DaemonRunner(object):
    """ A class for wrapping Python classes inside daemons, which can then be deployed as systemd
        services. Some resources used in developing this class and its peers were:

        http://nullege.com/codes/show/src%40p%40y%40pysrs-0.30.11%40SRS%40Daemon.py/87/SocketServer.UnixStreamServer/python
        http://www.velocityreviews.com/forums/t547449-unix-domain-socket-in-python-example.html
        http://0pointer.de/public/systemd-man/systemd.exec.html
        http://fedoraproject.org/wiki/Packaging:Systemd#.5BService.5D
        http://pypi.python.org/pypi/python-daemon/
        http://patrakov.blogspot.com/2011/01/writing-systemd-service-files.html
        http://www.python.org/dev/peps/pep-3143/ """

#===================================================================================================
#                                                                                       C L A S S

    _FAIL_LIMIT = 5

#___________________________________________________________________________________________________ __init__
    def __init__(self, targetClass, isSocket =False, **kwargs):

        self._logger = targetClass.getLogger()

        try:
            self._verbose = targetClass.VERBOSE
        except Exception as err:
            self._logger.write('Failed to acquire VERBOSE from ' + str(targetClass.__name__), err)
            sys.exit(126)

        try:
            self._uid = targetClass.SERVICE_UID
        except Exception as err:
            self._logger.write('Failed to acquire SERVICE_UID from ' + str(targetClass.__name__), err)
            sys.exit(126)

        if isSocket:
            self._wait = 0
        else:
            try:
                self._wait = targetClass.WAIT_INTERVAL
            except Exception as err:
                self._logger.write(
                    'Failed to acquire WAIT_INTERVAL from ' + str(targetClass.__name__), err )
                sys.exit(126)

        if isSocket:
            from pyaid.system.service.systemd.SystemSocketDaemon import SystemSocketDaemon
            self._targetClass = SystemSocketDaemon
            self._socketClass = targetClass
        else:
            self._targetClass = targetClass
            self._socketClass = None

        self._terminated  = False
        self._failCount   = 0
        self._target      = None

        self._workPath = os.path.join(targetClass.WORK_PATH, self._uid)
        self._pidPath  = os.path.join(targetClass.RUN_PATH, self._uid + '.pid')
        self._context  = daemon.DaemonContext(
            working_directory=ArgsUtils.get('workPath', self._workPath, kwargs),
            umask=ArgsUtils.get('umask', 0o000, kwargs),
            uid=ArgsUtils.get('uid', os.getuid(), kwargs),
            gid=ArgsUtils.get('gid', os.getgid(), kwargs),
            detach_process=True,
            pidfile=lockfile.FileLock(self._pidPath) )

        self._context.signal_map = {
            signal.SIGQUIT: self._handleQuit,
            signal.SIGTERM: self._handleCleanup,
            signal.SIGHUP: self._handleQuit,
            signal.SIGUSR1: self._handleUser }

        self._logger.write(self._uid + ' daemon initialized')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: uid
    @property
    def uid(self):
        return self._uid

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ terminate
    def terminate(self):
        self._terminated = True
        self._logger.write('Terminating: ' + self._uid)

        if os.path.exists(self._pidPath):
            os.remove(self._pidPath)

        try:
            if self._target:
                self._target.cleanup()
        except Exception as err:
            pass

        sys.exit(0)

#___________________________________________________________________________________________________ __del__
    def __del__(self):
        if self._terminated:
            return

        if os.path.exists(self._pidPath):
            os.remove(self._pidPath)

#___________________________________________________________________________________________________ initialize
    def initialize(self):
        if not os.path.exists(self._workPath):
            os.makedirs(self._workPath)

        if self._verbose:
            self._logger.write('Initialization complete.')

#___________________________________________________________________________________________________ run
    def run(self):
        self.initialize()

        self._logger('running now:')
        with self._context:
            self._logger.write('Daemon process detachment complete for ' + self._uid)
            if not self._createPIDFile():
                self.terminate()

            self._logger.write('Beginning daemon process ' + self._uid)
            self._target = self._createDaemon()
            if self._target is None:
                self.terminate()
                return

            if self._verbose:
                self._logger.write('Created daemon instance: ' + str(self._target))
            while True:
                try:
                    res = self._target()
                    if not res or self._target.terminated:
                        if self._verbose:
                            self._logger.write('Terminated by: %s [signal: %s | state: %s]' % (
                                self._targetClass.__name__, str(res),
                                str(self._target.terminated) ))
                        self.terminate()
                except Exception as err:
                    self._logger.writeError(self._uid + ' execution failure', err)
                    self._failCount += 1
                    if self._failCount > DaemonRunner._FAIL_LIMIT:
                        self._logger.write(self._uid + ' failed too many times. Shutting down.')
                        self.terminate()

                    self._target = self._createDaemon()
                    if self._target is None:
                        self.terminate()
                        return

                if self._wait:
                    time.sleep(self._wait)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createDaemon
    def _createDaemon(self):
        try:
            if self._socketClass:
                return self._targetClass(self, self._socketClass)

            return self._targetClass(self)
        except Exception as err:
            self._logger.writeError('Failed to instantiate Daemon class', err)

        return None

#___________________________________________________________________________________________________ _createPIDFile
    def _createPIDFile(self):
        try:
            f = open(self._pidPath, 'w')
            f.write(str(os.getpid()))
            f.close()
            return True
        except Exception as err:
            self._logger.writeError('Failure to write PID service file', err)
            return False

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleCleanup
    def _handleCleanup(self, signum, frame):
        self._logger.write(self._uid + ' cleaned up')

#___________________________________________________________________________________________________ _handleUser
    def _handleUser(self, signum, frame):
        self._logger.write(self._uid + ' received a user signal.')

#___________________________________________________________________________________________________ _handleQuit
    def _handleQuit(self, signum, frame):
        self._logger.write(self._uid + ' received SIGQUIT termination signal')
        self.terminate()

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ main
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.description = 'The runner class that handles turning a Python callable class into a' \
        + ' service daemon for use on Fedora systems and other linux flavors that use systemd' \
        + ' for service management.'

    #-------------------------------------------------------------------------------------------
    # Positional Arguments
    parser.add_argument(
        'package', dest='package', type=str,
        help='Absolute Python class package to be called for the daemon service execution')

    #-------------------------------------------------------------------------------------------
    # Optional Arguments
    parser.add_argument(
        '-s', '--socket', dest='socket', action='store_true', default=False,
        help='Runs the daemon class as a socket handler inside the SystemSocketDaemon instead' \
            + ' of running the class directly as a daemon.')

    args = parser.parse_args()

    parts = args.target.split('.')
    res         = __import__('.'.join(parts[:-1]), globals(), locals(), [parts[-1]])
    targetClass = getattr(res, parts[-1])

    c = DaemonRunner(targetClass, isSocket=args.socket)
    c.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    main()
