# UrlObject.py
# (C)2013
# Scott Ernst

import urllib

try:
    import urlparse
except Exception:
    import urllib.parse as urlparse

#___________________________________________________________________________________________________ UrlObject
class UrlObject(object):
    """A URL management class allowing for easy parsing and modification of a URL."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, sourceUrl =None):
        """Creates a new instance of UrlObject."""
        self._protocol = u''
        self._hostName = u''
        self._path     = u''
        self._fragment = u''
        self._params = dict()

        if sourceUrl:
            self.url = sourceUrl

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: protocol
    @property
    def protocol(self):
        return self._protocol
    @protocol.setter
    def protocol(self, value):
        self._protocol = value

#___________________________________________________________________________________________________ GS: hostName
    @property
    def hostName(self):
        return self._hostName
    @hostName.setter
    def hostName(self, value):
        self._hostName = value

#___________________________________________________________________________________________________ GS: path
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, value):
        self._path = value

#___________________________________________________________________________________________________ GS: params
    @property
    def params(self):
        return self._params
    @params.setter
    def params(self, value):
        self._params = value

#___________________________________________________________________________________________________ GS: queryString
    @property
    def queryString(self):
        return urllib.urlencode(self._params, True) if self._params else u''
    @queryString.setter
    def queryString(self, value):
        self._params = urlparse.parse_qs(value) if value else u''

#___________________________________________________________________________________________________ GS: fragment
    @property
    def fragment(self):
        return self._fragment
    @fragment.setter
    def fragment(self, value):
        self._fragment = value

#___________________________________________________________________________________________________ GS: url
    @property
    def url(self):
        return urlparse.urlunsplit((
            self._protocol,
            self._hostName,
            self._path,
            self.queryString,
            self._fragment ))
    @url.setter
    def url(self, value):
        parts = urlparse.urlsplit(value) if value else u''
        self._protocol = parts.scheme if parts else u''
        self._hostName = parts.netloc if parts else u''
        self._path     = parts.path if parts else u''
        self._fragment = parts.fragment if parts else u''

        query = parts.query if parts else u''
        if query:
            self._params = urlparse.parse_qs(query, True)
        else:
            self._params = dict()

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return self.url

