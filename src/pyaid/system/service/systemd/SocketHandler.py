# SocketHandler.py
# (C)2012-2014
# Scott Ernst

try:
    import urllib2
    unquote = urllib2.unquote
except Exception:
    import urllib.parse as urllib_parse
    unquote = urllib_parse.unquote

try:
    import SocketServer
except Exception:
    import socketserver
    SocketServer = socketserver

from pyaid.debug.Logger import Logger
from pyaid.json.JSON import JSON

#___________________________________________________________________________________________________ SocketHandler
class SocketHandler(SocketServer.StreamRequestHandler):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    SERVICE_UID   = 'test'
    VERBOSE       = False
    WORK_PATH     = '/var/lib/'
    RUN_PATH      = '/var/run/'
    LOG_PATH      = '/var/log/'

#___________________________________________________________________________________________________ __init__
    def __init__(self, request, client_address, server):
        self._log = Logger(self)
        self._log.write('Socket handler created')

        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: returnResponse
    @property
    def returnResponse(self):
        return getattr(self.__class__, 'RETURN_RESPONSE', False)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ handle
    def handle(self):
        try:
            data = self.rfile.readline().strip()
            self._log.write('HANDLE: ' + str(data))
            try:
                result = self._respondImpl(JSON.fromString(unquote(data)))
            except Exception as err:
                self._log.writeError('RESPOND FAILURE', err)
                if self.returnResponse:
                    self.wfile.write(JSON.asString({'error':1}))
                return

            if self.returnResponse:
                out = {'error':0}
                if result:
                    out['payload'] = result
                self.wfile.write(out)
        except Exception as err:
            self._log.write('HANDLE FAILURE', err)

        return

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _respondImpl
    def _respondImpl(self, data):
        pass
