# SystemUtils.py
# (C)2012-2013
# Scott Ernst

import subprocess

#___________________________________________________________________________________________________ SystemUtils
class SystemUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ executeCommand
    @classmethod
    def executeCommand(cls, cmd, remote =False, shell =True, wait =False):
        if shell and isinstance(cmd, list):
            cmd = ' '.join(cmd)

        if remote:
            pipe = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=None,
                stderr=None,
                stdin=None,
                close_fds=False
            )
            if wait:
                pipe.wait()
            return {'error':'', 'out':'', 'code':0, 'command':cmd}

        pipe = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if wait:
            pipe.wait()
        out, error = pipe.communicate()
        result = {'error':error, 'out':out, 'code':pipe.returncode, 'command':cmd}
        return result
