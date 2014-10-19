# TimeUtils.py
# (C)2011-2014
# Scott Ernst and Eric David Wills

import time
import calendar
from datetime import datetime, timedelta

from pyaid.radix.Base36 import Base36
from pyaid.radix.Base64 import Base64

#___________________________________________________________________________________________________ TimeUtils
class TimeUtils(object):
    """A class for time utilities."""

    ZULU_PRECISE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

#___________________________________________________________________________________________________ secondsToDurationTimecode
    @classmethod
    def secondsToDurationTimecode(cls, seconds):
        """ Turns the specified number of seconds (including fractional seconds) into a durational
            timecode of the format HH:MM:SS.000 """

        time    = seconds
        hours   = int(float(time)/3600.0)
        time   -= 3600*hours
        mins    = int(float(time)/60.0)
        time   -= 60*mins
        secs    = int(float(time))
        time   -= secs
        millis  = int(round(float(time)*1000.0))

        return unicode(hours).zfill(2) + u':' \
            + unicode(mins).zfill(2) + u':' \
            + unicode(secs).zfill(2) + u'.' \
            + unicode(millis).zfill(3)

#___________________________________________________________________________________________________ utcToLocalDatetime
    @classmethod
    def utcToLocalDatetime(cls, utcDatetime):
        return cls.secondsToDatetime(
            cls.datetimeToSeconds(utcDatetime) - (time.altzone if time.daylight else time.timezone))

#___________________________________________________________________________________________________ getFriendlyTimestamp
    @staticmethod
    def getFriendlyTimestamp(timestamp, timeZoneOffset =0):
        """ Returns a friendly, human readable date for the last time the item was updated if an
            upts is part of the model. If not an empty string is returned instead.

            @@@param timestamp:datetime
                A datetime object that represents the date/time you want converted to a friendly
                display format.

            @@@param timeZoneOffset:int
                Offset, in minutes, that should be subtracted from UTC time. Used to adjust to a
                local time zone for display. For example, a value of -120 would specify the GMT +2
                timezone, which is two hours ahead of GMT. Similarly, the PST time would be 480. """

        if not isinstance(timestamp, datetime):
            return ''

        # Adjust for local timezone if one is specified
        tzOff = timedelta(minutes=timeZoneOffset)
        upts  = timestamp - tzOff
        now   = datetime.utcnow() - tzOff

        # Handles different years
        if upts.year != now.year:
            return '%s/%s/%s' % (str(upts.month), str(upts.day), str(upts.year))

        # Handles different months
        if upts.month != now.month:
            return upts.strftime('%b') + ' ' + str(upts.day)

        nowYearday  = int(now.strftime('%j'))
        uptsYearday = int(upts.strftime('%j'))

        # Handles same day
        if nowYearday == uptsYearday:
            return upts.strftime('%I:%M%p')

        # Handles same week
        if nowYearday - uptsYearday < 7:
            return upts.strftime('%a %I:%M%p')

        # Handles earlier the same month
        return upts.strftime('%b') + ' ' + str(upts.day) + ', ' + upts.strftime('%I:%M%p')

#___________________________________________________________________________________________________ serializeToList
    @staticmethod
    def serializeToList(timestamp):
        return [
            timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute,
            timestamp.second, timestamp.microsecond ]

#___________________________________________________________________________________________________ parseSerialList
    @staticmethod
    def parseSerialList(timeList):
        return datetime(
            year=timeList[0], month=timeList[1], day=timeList[2],
            hour=timeList[3], minute=timeList[4], second=timeList[5], microsecond=timeList[6])

#___________________________________________________________________________________________________ getSolrTimestamp
    @staticmethod
    def getSolrTimestamp(timestamp):
        return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

#___________________________________________________________________________________________________ getAWSTimestamp
    @classmethod
    def getAWSTimestamp(cls, timestamp):
        return cls.toZuluPreciseTimestamp(timestamp)

#___________________________________________________________________________________________________ toZuluPreciseTimestamp
    @classmethod
    def toZuluPreciseTimestamp(cls, source =None):
        if not source:
            source = datetime.utcnow()
        return source.strftime(cls.ZULU_PRECISE_FORMAT)

#___________________________________________________________________________________________________ fromZuluPreciseTimestamp
    @classmethod
    def fromZuluPreciseTimestamp(cls, dateString):
        datetime.strptime(dateString, cls.ZULU_PRECISE_FORMAT)

#___________________________________________________________________________________________________ getNowSeconds
    @staticmethod
    def getNowSeconds():
        """ Returns the current number of seconds since the Unix Epoch

            @return int """

        return int(calendar.timegm(datetime.utcnow().utctimetuple()))

#___________________________________________________________________________________________________ getNowMacintoshSeconds
    @classmethod
    def getNowMacintoshSeconds(cls):
        """ Returns the current number os seconds since the Apple Macintosh Epoch
            of January 1, 1904.

            QuickTime movies and other Apple formats store date and time information in Macintosh
            date format: a 32-bit value indicating the number of seconds that have passed since
            midnight January 1, 1904. This value does not specify a time zone. Common practice is
            to use local time for the time zone where the value is generated. It is strongly
            recommended that all calendar date and time values be stored using UTC time, so that
            all files have a time and date relative to the same time zone.

            @return int """

        delta = datetime.utcnow() - datetime(1904, 1, 1)
        return int(delta.total_seconds())

#___________________________________________________________________________________________________ getNowHours
    @classmethod
    def getNowMinutes(cls):
        """ Returns the number of minutes since the Unix Epoch """
        return float(cls.getNowSeconds())/60.0

#___________________________________________________________________________________________________ getNowHours
    @classmethod
    def getNowHours(cls):
        """ Returns the number of hours since the Unix Epoch """
        return float(cls.getNowSeconds())/3600.0

#___________________________________________________________________________________________________ getNowDatetime
    @staticmethod
    def getNowDatetime(offsetSeconds =None):
        """ Returns the current datetime.

            @@@return datetime
        """

        dt = datetime.utcnow()
        if offsetSeconds:
            dt += timedelta(seconds=offsetSeconds)
        return dt

#___________________________________________________________________________________________________ datetimeToSeconds
    @staticmethod
    def datetimeToSeconds(dt):
        """ Returns the number of seconds since the Unix Epoch for the specified datetime.

            @@@param dt:Datetime
                The datetime object to convert into seconds.

            @@@return int
        """

        return calendar.timegm(dt.utctimetuple())

#___________________________________________________________________________________________________ timecodeToDatetime
    @classmethod
    def timecodeToDatetime(cls, timeCode, baseTime =0):
        """ Returns the datetime object that represents the given Base64 timeCode for the given
            base time, which by default is 0.
        """
        return cls.secondsToDatetime(Base64.from64(timeCode) + baseTime)

#___________________________________________________________________________________________________ datetimeToTimecode
    @classmethod
    def datetimeToTimecode(cls, dt, baseTime =0):
        """ Returns a timecode (base64 encoded seconds string) for the given datetime object and
            offset by the baseTime number of seconds.
        """
        return Base64.to64(cls.datetimeToSeconds(dt) - baseTime)

#___________________________________________________________________________________________________ getNowTimecode
    @classmethod
    def getNowTimecode(cls, baseTime =0):
        return Base64.to64(cls.getNowSeconds() - baseTime)

#___________________________________________________________________________________________________ getNowTimecode36
    @classmethod
    def getNowTimecode36(cls, baseTime =0):
        return Base36.to36(cls.getNowSeconds() - baseTime)

#___________________________________________________________________________________________________ getUidTimecode
    @classmethod
    def getUidTimecode(cls, prefix =None, suffix =None):
        """ Creates a timecode down to the microsecond for use in creating unique UIDs. """
        out = Base64.to64(cls.getNowSeconds()) + u'-' + Base64.to64(datetime.microsecond)

        return ((unicode(prefix) + u'-') if prefix else u'') + out \
            + ((u'-' + unicode(suffix)) if suffix else u'')

#___________________________________________________________________________________________________ timecodeToFriendlyTimestamp
    @classmethod
    def timecodeToFriendlyTimestamp(cls, timeCode, baseTime =0):
        return cls.getFriendlyTimestamp(cls.timecodeToDatetime(timeCode, baseTime))

#___________________________________________________________________________________________________ secondsToDatetime
    @staticmethod
    def secondsToDatetime(s, isUtc =True):
        """ Returns a datetime for the specified number of seconds since the Unix Epoch.

            @@@param s:int
                Number of seconds to convert.

            @@@return datetime
        """
        if isUtc:
            return datetime.utcfromtimestamp(s)
        return datetime.fromtimestamp(s)

#___________________________________________________________________________________________________ getAWSAccessTimestamp
    @staticmethod
    def awsAccessToDateTime(s):
        parts  = s.split()
        offset = timedelta(hours=int(s[1])/100) if len(parts) > 1 else timedelta(0)
        return datetime.strptime(parts[0], '%d/%b/%Y:%H:%M:%S') + offset

#___________________________________________________________________________________________________ cfAccessToDateTime
    @staticmethod
    def cfAccessToDateTime(s):
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

#___________________________________________________________________________________________________ dateTimeToRssTimestamp
    @staticmethod
    def dateTimeToRssTimestamp(dt):
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

#___________________________________________________________________________________________________ dateTimeToWebTimestamp
    @staticmethod
    def dateTimeToWebTimestamp(dt):
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

#___________________________________________________________________________________________________ webTimestampToDateTime
    @staticmethod
    def webTimestampToDateTime(ts):
        return datetime.strptime(ts, '%a, %d %b %Y %H:%M:%S GMT')

#___________________________________________________________________________________________________ getUtcTagTimestamp
    @staticmethod
    def getUtcTagTimestamp(dt =None):
        if not dt:
            dt = datetime.utcnow()
        return dt.strftime('%Y%m%d%H%M%S')

#___________________________________________________________________________________________________ toPrettyTime
    @classmethod
    def toPrettyElapsedTime(cls, elapsedMilliseconds):
        """ Returns a pretty elapsed time based on the number of milliseconds elapsed argument. """
        t = elapsedMilliseconds
        if t == 0:
            return u'0'

        hasMinutes = False
        hasSeconds = False

        out = u''
        if t >= 60000:
            hasMinutes = True
            cVal  = int(float(t)/60000.0)
            s     = unicode(cVal)
            t -= cVal*60000

            if t == 0:
                return s + u' min' + (u's' if cVal > 1 else u'')

            s = s.zfill(2)
            out  += s + u':'

        if t >= 1000:
            hasSeconds = True
            cVal  = int(float(t)/1000.0)
            s     = unicode(cVal)
            t -= cVal*1000

            if t == 0 and not hasMinutes:
                return s + u' sec' + (u's' if cVal > 1 else u'')

            s = s.zfill(2)
            out += s
        elif hasMinutes:
            out += u'00'

        if t == 0:
            return out

        s = unicode(round(t))
        if not hasMinutes and not hasSeconds:
            return s + u' ms'

        s = s.zfill(2)
        return out + u'.' + s
