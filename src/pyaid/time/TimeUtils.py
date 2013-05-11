# TimeUtils.py
# (C)2011-2013
# Scott Ernst and Eric David Wills

import time
import calendar
from datetime import datetime, timedelta

from pyaid.radix.Base64 import Base64

#___________________________________________________________________________________________________ TimeUtils
class TimeUtils(object):
    """A class for time utilities."""

#___________________________________________________________________________________________________ utcToLocalDatetime
    @classmethod
    def utcToLocalDatetime(cls, utcDatetime):
        return cls.secondsToDatetime(
            cls.datetimeToSeconds(utcDatetime) - (time.altzone if time.daylight else time.timezone)
        )

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
                timezone, which is two hours ahead of GMT. Similarly, the PST time would be 480.
        """

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
            timestamp.second, timestamp.microsecond
        ]

#___________________________________________________________________________________________________ parseSerialList
    @staticmethod
    def parseSerialList(timeList):
        return datetime(
            year=timeList[0],
            month=timeList[1],
            day=timeList[2],
            hour=timeList[3],
            minute=timeList[4],
            second=timeList[5],
            microsecond=timeList[6]
        )

#___________________________________________________________________________________________________ getSolrTimestamp
    @staticmethod
    def getSolrTimestamp(timestamp):
        return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

#___________________________________________________________________________________________________ getAWSTimestamp
    @staticmethod
    def getAWSTimestamp(timestamp):
        return timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')

#___________________________________________________________________________________________________ getNowSeconds
    @staticmethod
    def getNowSeconds():
        """Returns the current number of seconds since the Unix Epoch.
        @return int
        """

        return int(calendar.timegm(datetime.utcnow().utctimetuple()))

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

#___________________________________________________________________________________________________ timecodeToFriendlyTimestamp
    @classmethod
    def timecodeToFriendlyTimestamp(cls, timeCode, baseTime =0):
        return cls.getFriendlyTimestamp(cls.timecodeToDatetime(timeCode, baseTime))

#___________________________________________________________________________________________________ secondsToDatetime
    @staticmethod
    def secondsToDatetime(s):
        """ Returns a datetime for the specified number of seconds since the Unix Epoch.

            @@@param s:int
                Number of seconds to convert.

            @@@return datetime
        """

        return datetime.utcfromtimestamp(s)

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
