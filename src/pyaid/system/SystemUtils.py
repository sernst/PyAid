# SystemUtils.py
# (C)2012
# Scott Ernst

import subprocess

#___________________________________________________________________________________________________ SystemUtils
class SystemUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ executeCommand
    @classmethod
    def executeCommand(cls, cmd, remote =False):
        if isinstance(cmd, list):
            cmd = ' '.join(cmd)

        if remote:
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=None,
                stderr=None,
                stdin=None,
                close_fds=False
            )
            return {'error':'', 'out':'', 'code':0}

        pipe = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, error = pipe.communicate()
        return {'error':error, 'out':out, 'code':pipe.returncode}
