# S3Bucket.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function

import os
import gzip
import tempfile

from boto import s3
from boto.s3.connection import Location
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

    LOCATIONS   = Location
    PUBLIC_READ = 'public-read'
    PRIVATE     = 'private'

    _UPLOAD_CONDITIONS = [
        u'{"bucket":"%(bucket)s"}',
        u'{"acl":"private"}',
        u'{"key":"%(key)s"}',
        u'{"success_action_status":"200"}',
        u'["content-length-range", 0, %(maxSize)s]',
        u'{"x-amz-meta-uuid": "14365123651274"}',
        u'["starts-with", "$x-amz-meta-tag", ""]',
        u'{"x-amz-algorithm": "AWS4-HMAC-SHA256"}',
        u'{"x-amz-credential": "%(awsid)/%{isoDate}/%{region}/s3/aws4_request"}'
        u'{"x-amz-date": "%{isoDate}T000000Z" }']

    _UPLOAD_POLICY = u'{"expiration":"%s", "conditions":[%s]}'

#___________________________________________________________________________________________________ __init__
    def __init__(self, bucketName, awsId, awsSecret, location =None):
        """Creates a new instance of S3Bucket."""
        self._bucketName = bucketName
        self._awsId      = awsId
        self._awsSecret  = awsSecret

        if location:
            self._conn = s3.connect_to_region(location, )

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

#___________________________________________________________________________________________________ generateUrl
    def generateUrl(self, keyName, secure =True, expires =0, expiresInHours =0, expiresInDays =0):
        """ Creates a url for the specified key name that expires in the specified number of
            seconds. Alternatively you can specify the expiresInHours or expiresInDays for easy
            conversion to alternate time periods. """
        if not expires:
            if expiresInHours:
                expires = int(3600.0*float(expiresInHours))
            elif expiresInDays:
                expires = int(24.0*3600.0*float(expiresInDays))

        if expires == 0:
            proto = 'http'
            if secure:
                proto += 's'
            return proto + '://' + self._bucket.get_website_endpoint() + '/' + keyName.lstrip('/')

        key = self.getKey(keyName, createIfMissing=True)
        return key.generate_url(
            expires_in=expires,
            query_auth=bool(expires > 0),
            force_http=not secure)

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
            StringUtils.toUnicode(len(out)),
            self._bucketName,
            StringUtils.toUnicode(path))
        if logger:
            logger.write(s)
        else:
            print(s)

        index = 0
        for obj in out:
            s = u'  ' + StringUtils.toUnicode(index) + u' - ' + obj.name
            if logger:
                logger.write(s)
            else:
                print(s)
            index += 1

#___________________________________________________________________________________________________ getKey
    def getKey(self, key, createIfMissing =True):
        if StringUtils.isStringType(key):
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

        contents = StringUtils.toUnicode(contents)

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
            policy =None, zipContents =False
    ):
        k = self.getKey(key)

        if not self._localIsNewer(k, newerThanDate):
            return False

        headers = self._generateHeaders(k.name, expires=expires, eTag=eTag, maxAge=maxAge)

        if zipContents:
            with open(filename, 'r') as f:
                contents = f.read()

            fd, tempPath = tempfile.mkstemp()
            with gzip.open(tempPath, 'w+b') as f:
                f.write(contents.encode('utf-8', 'ignore'))

            headers['Content-Encoding'] = 'gzip'
            filename = tempPath

            k.set_contents_from_filename(filename=filename, headers=headers, policy=policy)

            os.close(fd)
            if os.path.exists(tempPath):
                os.remove(tempPath)
            return True

        k.set_contents_from_filename(filename=filename, headers=headers, policy=policy)
        return True

#___________________________________________________________________________________________________ generateExpiresUrl
    def generateExpiresUrl(self, key, expiresAtDateTime, secure =True):
        delta = TimeUtils.datetimeToSeconds(expiresAtDateTime) - TimeUtils.getNowSeconds()
        return self._bucket.get_key(key_name=key).generate_url(
            expires_in=delta,
            force_http=not secure)

#___________________________________________________________________________________________________ createUploadPolicy
    def createUploadPolicy(self, key, durationSeconds, maxSizeBytes):
        """Returns a S3 upload policy and signature for this bucket with the specified key. """
        return self._conn.build_post_form_args(
            bucket_name=self.bucketName,
            key=key,
            expires_in=durationSeconds,
            acl='private',
            max_content_length=maxSizeBytes)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _generateHeaders
    @classmethod
    def _generateHeaders(cls, keyName, expires =None, eTag =None, maxAge =-1):
        """Doc..."""
        headers = dict()

        if expires:
            if StringUtils.isStringType(expires):
                headers['Expires'] = StringUtils.toStr2(expires)
            elif isinstance(expires, str):
                headers['Expires'] = expires
            else:
                headers['Expires'] = TimeUtils.dateTimeToWebTimestamp(expires)
        elif eTag:
            headers['ETag'] = StringUtils.toUnicode(eTag)

        if maxAge > -1:
            headers['Cache-Control'] = 'public, max-age=' + StringUtils.toUnicode(maxAge)

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
    @classmethod
    def _localIsNewer(cls, key, newerThanDate):
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
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__


