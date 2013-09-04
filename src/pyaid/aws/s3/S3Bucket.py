# S3Bucket.py
# (C)2013
# Scott Ernst

import os
import gzip
import tempfile

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from pyaid.enum.MimeTypeEnum import MIME_TYPES
from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.time.TimeUtils import TimeUtils

#___________________________________________________________________________________________________ S3Bucket
class S3Bucket(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    PUBLIC_READ = 'public-read'
    PRIVATE     = 'private'

#___________________________________________________________________________________________________ __init__
    def __init__(self, bucketName, awsId, awsSecret):
        """Creates a new instance of S3Bucket."""
        self._bucketName = bucketName
        self._awsId      = awsId
        self._awsSecret  = awsSecret

        self._conn   = S3Connection(self._awsId, self._awsSecret)
        self._bucket = Bucket(self._conn, bucketName)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: bucketName
    @property
    def bucketName(self):
        return self._bucketName

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ listKeys
    def listKeys(self, path, pathFilter =None, includeDirs =True, includeFiles =True):
        if len(path) > 0 and path[0] == '/':
            path = path[1:]

        objs = self._bucket.list(path)
        out  = []
        for obj in objs:
            isDir = obj.name[-1] == '/' and obj.size == 0
            if isDir and not includeDirs:
                continue
            if not isDir and not includeFiles:
                continue

            if pathFilter is None or obj.name.find(pathFilter) != -1:
                out.append(obj)

        return out

#___________________________________________________________________________________________________ printBucketContents
    def printBucketContents(self, path, fileFilter, logger =None):
        out = self.listKeys(path, fileFilter)
        s = u'Displaying %s results for %s/%s.' % (
            unicode(len(out)),
            self._bucketName,
            unicode(path))
        if logger:
            logger.write(s)
        else:
            print s

        index = 0
        for obj in out:
            s = u'  ' + unicode(index) + u' - ' + obj.name
            if logger:
                logger.write(s)
            else:
                print s
            index += 1

#___________________________________________________________________________________________________ getKey
    def getKey(self, key, createIfMissing =True):
        if isinstance(key, basestring):
            out = self._bucket.get_key(key_name=key)
            if createIfMissing and not out:
                out = Key(self._bucket, key)
            return out

        return key

#___________________________________________________________________________________________________ put
    def put(
            self, key, contents, zipContents =False, maxAge =-1, eTag =None, expires =None,
            newerThanDate =None, policy =None
    ):
        """Doc..."""
        k = self.getKey(key)

        if not self._localIsNewer(k, newerThanDate):
            return False

        headers = self._generateHeaders(k.name, expires=expires, eTag=eTag, maxAge=maxAge)

        if not isinstance(contents, unicode):
            contents = contents.decode('utf-8', 'ignore')

        if zipContents:
            fd, tempPath = tempfile.mkstemp()
            f = gzip.open(tempPath, 'w+b')
            f.write(contents.encode('utf-8', 'ignore'))
            f.close()

            headers['Content-Encoding'] = 'gzip'
            k.set_contents_from_filename(filename=tempPath, headers=headers, policy=policy)

            os.close(fd)
            if os.path.exists(tempPath):
                os.remove(tempPath)
            return True

        k.set_contents_from_string(contents, headers=headers, policy=policy)
        return True

#___________________________________________________________________________________________________ putFile
    def putFile(
            self, key, filename, maxAge =-1, eTag =None, expires =None, newerThanDate =None,
            policy =None
    ):
        k = self.getKey(key)

        if not self._localIsNewer(k, newerThanDate):
            return False

        headers = self._generateHeaders(k.name, expires=expires, eTag=eTag, maxAge=maxAge)
        k.set_contents_from_filename(filename=filename, headers=headers, policy=policy)
        return True

#___________________________________________________________________________________________________ generateExpiresUrl
    def generateExpiresUrl(self, key, expiresAtDateTime):
        delta = TimeUtils.datetimeToSeconds(expiresAtDateTime) - TimeUtils.getNowSeconds()
        return self._bucket.get_key(key_name=key).generate_url(expires_in=delta, force_http=True)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _generateHeaders
    def _generateHeaders(self, keyName, expires =None, eTag =None, maxAge =-1):
        """Doc..."""
        headers = dict()

        if expires:
            if isinstance(expires, unicode):
                headers['Expires'] = expires.encode('utf-8', 'ignore')
            elif isinstance(expires, str):
                headers['Expires'] = expires
            else:
                headers['Expires'] = TimeUtils.dateTimeToWebTimestamp(expires)
        elif eTag:
            headers['ETag'] = unicode(eTag)

        if maxAge > -1:
            headers['Cache-Control'] = 'public, max-age=' + unicode(maxAge)

        if keyName.endswith('.jpg'):
            contentType = MIME_TYPES.JPEG_IMAGE
        elif keyName.endswith('.png'):
            contentType = MIME_TYPES.PNG_IMAGE
        elif keyName.endswith('.gif'):
            contentType = MIME_TYPES.GIF_IMAGE
        else:
            contentType = FileUtils.getMimeType(keyName)
        if StringUtils.begins(contentType, ('text/', 'application/')):
            headers['Content-Type'] = contentType + '; charset=UTF-8'
        else:
            headers['Content-Type'] = contentType

        return headers

#___________________________________________________________________________________________________ _localIsNewer
    def _localIsNewer(self, key, newerThanDate):
        if not newerThanDate or not key.last_modified:
            return True
        return TimeUtils.webTimestampToDateTime(key.last_modified) < newerThanDate

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__


