# TimeUtils.py
# (C)2011-2015
# Scott Ernst and Eric David Wills

from __future__ import print_function, absolute_import, unicode_literals, division

import math
import time
import calendar
from datetime import datetime, timedelta
from datetime import time as dtTime

from pyaid.radix.Base36 import Base36
from pyaid.radix.Base64 import Base64
from pyaid.string.StringUtils import StringUtils


#___________________________________________________________________________________________________ TimeUtils
class TimeUtils(object):
    """A class for time utilities."""

#===================================================================================================
#                                                                                       C L A S S

    YEARS           = 'years'
    MONTHS          = 'months'
    WEEKS           = 'weeks'
    DAYS            = 'days'
    HOURS           = 'hours'
    MINUTES         = 'mins'
    SECONDS         = 'secs'
    MILLISECONDS    = 'msecs'
    MICROSECONDS    = 'micros'

    ISO_8601_DATE = '%Y-%m-%d'
    ISO_8601_WEEK = '%Y-W%W'
    ISO_8601_WEEK_DATE = '%Y-W%W-%d'
    ISO_8601_ORDINAL_DATE = '%Y-%j'
    ORDINAL_DATE_SHORT = '%y-%j'

    ZULU_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    _ZULU_PRECISE_FORMAT = '%Y-%m-%dT%H:%M:%S'

#___________________________________________________________________________________________________ getHttpRfc1132Timestamp
    @classmethod
    def getHttpHeaderTimestamp(cls, dt):
        """ Return a string representation of a date according to RFC 1123 (HTTP/1.1). The supplied
            date is assumed to be utc. """

        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
            dt.year, dt.hour, dt.minute, dt.second)

#___________________________________________________________________________________________________ getElapsedSeconds
    @classmethod
    def getElapsedTime(cls, startDateTime, endDateTime, toUnit =SECONDS):
        """ Calculates the time elapsed between two datetime objects and returns the value as a
            floating point number in the specified unit. """
        s = startDateTime
        e = endDateTime
        delta = endDateTime - startDateTime

        seconds = delta.total_seconds()
        if toUnit == cls.SECONDS:
            return seconds
        return cls.fromSeconds(seconds, toUnit)

#___________________________________________________________________________________________________ toSeconds
    @classmethod
    def toSeconds(cls, value, fromUnit):
        """toSeconds doc..."""
        value = float(value)
        if fromUnit == cls.SECONDS:
            return value
        elif fromUnit == cls.MICROSECONDS:
            return value/1.0e6
        elif fromUnit == cls.MILLISECONDS:
            return value/1.0e3

        value *= 60.0
        if fromUnit == cls.MINUTES:
            return value

        value *= 60.0
        if fromUnit == cls.HOURS:
            return value

        value *= 24.0
        if fromUnit == cls.DAYS:
            return value

        if fromUnit == cls.WEEKS:
            return value*7.0

        elif fromUnit == cls.MONTHS:
            return value*(365.25/12.0)

        elif fromUnit == cls.YEARS:
            return value*365.25

        raise ValueError('Unrecognized fromUnit "%s"' % fromUnit)

#___________________________________________________________________________________________________ fromSeconds
    @classmethod
    def fromSeconds(cls, value, toUnit):
        """fromSeconds doc..."""
        value = float(value)
        if toUnit == cls.SECONDS:
            return value
        elif toUnit == cls.MICROSECONDS:
            return value*1.0e6
        elif toUnit == cls.MILLISECONDS:
            return value*1.0e3

        value /= 60.0
        if toUnit == cls.MINUTES:
            return value

        value /= 60.0
        if toUnit == cls.HOURS:
            return value

        value /= 24.0
        if toUnit == cls.DAYS:
            return value

        if toUnit == cls.WEEKS:
            return value/7.0

        elif toUnit == cls.MONTHS:
            return value/(365.25/12.0)

        elif toUnit == cls.YEARS:
            return value/365.25

        raise ValueError('Unrecognized toUnit "%s"' % toUnit)

#___________________________________________________________________________________________________ convert
    @classmethod
    def convert(cls, value, fromUnit, toUnit):
        """convert doc..."""
        return cls.fromSeconds(cls.toSeconds(value, fromUnit), toUnit)

#___________________________________________________________________________________________________ toFormat
    @classmethod
    def toFormat(cls, dateFormat, value =None, dateSeparator ='-', timeSeparator =':'):
        """toFormat doc..."""
        if not value:
            value = datetime.utcnow()
        return value.strftime(dateFormat.replace('-', dateSeparator).replace(':', timeSeparator))

#___________________________________________________________________________________________________ secondsSinceMidnight
    @classmethod
    def secondsSinceMidnight(cls, dt =None):
        """secondsSinceMidnight doc..."""
        if dt is None:
            dt = datetime.utcnow()
        return (datetime.combine(dt.date(), dtTime(0, 0)) - dt).seconds

#___________________________________________________________________________________________________ fromFormat
    @classmethod
    def fromFormat(cls, dateFormat, value, dateSeparator ='-', timeSeparator =':'):
        """fromFormat doc..."""
        return datetime.strptime(
            value, dateFormat.replace('-', dateSeparator).replace(':', timeSeparator))

#___________________________________________________________________________________________________ explodeElapsedTime
    @classmethod
    def explodeElapsedTime(cls, seconds):
        """explodeTime doc..."""
        t       = float(seconds)

        days    = int(t/(24.0*3600.0))
        t      -= 24.0*3600.0*float(days)

        hours   = int(t/3600.0)
        t      -= 3600.0*float(hours)

        mins    = int(t/60.0)
        secs    = t - 60.0*float(mins)


        return {'days':days, 'hours':hours, 'minutes':mins, 'seconds':secs}

#___________________________________________________________________________________________________ implodeElapsedTime
    @classmethod
    def implodeElapsedTime(cls, explodedTime):
        """implodeElapsedTime doc..."""
        d = explodedTime
        return 240.0*3600.0*float(d.get('days', 0.0)) + 3600.0*float(d.get('hours', 0.0)) \
            + 60.0*float(d.get('minutes', 0.0)) + float(d.get('seconds', 0.0))

#___________________________________________________________________________________________________ secondsToDurationTimecode
    @classmethod
    def secondsToDurationTimecode(cls, seconds):
        """ Turns the specified number of seconds (including fractional seconds) into a durational
            timecode of the format HH:MM:SS.000 """

        time = cls.explodeElapsedTime(seconds)
        secs    = int(time['seconds'])
        millis  = int(round(1000.0*(time['seconds'] - float(secs))))

        return StringUtils.toUnicode(time['hours']).zfill(2) + ':' \
            + StringUtils.toUnicode(time['minutes']).zfill(2) + ':' \
            + StringUtils.toUnicode(secs).zfill(2) + '.' \
            + StringUtils.toUnicode(millis).zfill(3)

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

#___________________________________________________________________________________________________ getAwsTimestampV4
    @classmethod
    def getAwsTimestampV4(cls, timestamp):
        """getAwsTimestampV4 doc..."""
        return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

#___________________________________________________________________________________________________ getAWSTimestamp
    @classmethod
    def getAWSTimestamp(cls, timestamp):
        return cls.toZuluPreciseTimestamp(timestamp)

#___________________________________________________________________________________________________ toZuluFormat
    @classmethod
    def toZuluFormat(cls, source =None):
        """toZuluFormat doc..."""
        if not source:
            source = datetime.utcnow()
        return  source.strftime(cls.ZULU_FORMAT)

#___________________________________________________________________________________________________ fromZuluFormat
    @classmethod
    def fromZuluFormat(cls, dateString):
        """fromZuluFormat doc..."""
        return datetime.strptime(dateString, cls.ZULU_FORMAT)

#___________________________________________________________________________________________________ toZuluPreciseTimestamp
    @classmethod
    def toZuluPreciseTimestamp(cls, source =None):
        if not source:
            source = datetime.utcnow()
        out = source.strftime(cls._ZULU_PRECISE_FORMAT)
        out + '.' + str(source.microsecond)[:3] + 'Z'
        return out

#___________________________________________________________________________________________________ fromZuluPreciseTimestamp
    @classmethod
    def fromZuluPreciseTimestamp(cls, dateString):
        quotient  = dateString[:-5]
        remainder = dateString[-4:-1] + '000'
        out = datetime.strptime(quotient, cls._ZULU_PRECISE_FORMAT)
        out.microsecond = int(remainder)
        return out

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

        # delta = dt - datetime.fromtimestamp(0)
        # return math.floor(delta.total_seconds())

        return calendar.timegm(dt.utctimetuple())

#___________________________________________________________________________________________________ timecodeToDatetime
    @classmethod
    def timecodeToDatetime(cls, timeCode, baseTime =0):
        """ Returns the datetime object that represents the given Base64 timeCode for the given
            base time, which by default is 0.
        """
        return cls.secondsToDatetime(Base64.from64(timeCode) + baseTime)

#___________________________________________________________________________________________________ secondsToTimeDelta
    @classmethod
    def secondsToTimeDelta(cls, seconds):
        """ Returns a timedelta object for the specified number of elapsed seconds using methods
            that prevent overflows of the constructor values for the timedelta object. """

        days = math.floor(seconds/(3600.0*24.0))
        seconds -= days*3600.0*24.0

        hours = math.floor(seconds/3600.0)
        seconds -= hours*3600.0

        minutes = math.floor(seconds/60.0)
        seconds -= minutes*60.0

        microseconds = 1.0e6*(seconds - math.floor(seconds))

        seconds = math.floor(seconds)

        return timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)

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
        out = Base64.to64(cls.getNowSeconds()) + '-' + Base64.to64(datetime.microsecond)

        return ((StringUtils.toUnicode(prefix) + '-') if prefix else '') + out \
            + (('-' + StringUtils.toUnicode(suffix)) if suffix else '')

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
        t = int(elapsedMilliseconds)
        if t == 0:
            return '0'

        hasMinutes = False
        hasSeconds = False

        out = ''
        if t >= 60000:
            hasMinutes = True
            cVal  = int(float(t)/60000.0)
            s     = StringUtils.toUnicode(cVal)
            t -= cVal*60000

            if t == 0:
                return s + ' min' + ('s' if cVal > 1 else '')

            s = s.zfill(2)
            out  += s + ':'

        if t >= 1000:
            hasSeconds = True
            cVal  = int(float(t)/1000.0)
            s     = StringUtils.toUnicode(cVal)
            t -= cVal*1000

            if t == 0 and not hasMinutes:
                return s + ' sec' + ('s' if cVal > 1 else '')

            s = s.zfill(2)
            out += s
        elif hasMinutes:
            out += '00'

        if t == 0:
            return out

        s = StringUtils.toUnicode(int(round(t)))
        if not hasMinutes and not hasSeconds:
            return s + ' ms'

        s = s.zfill(2)
        return out + '.' + s

#___________________________________________________________________________________________________ differsByDays
    @classmethod
    def differsByDays(cls, timeA, timeB, dayDelta):
        """ Computes the difference between the two datetime objects and returns a boolean, which
            is true if the absolute number of days between the two datetimes is greater than or
            equal to the specified delta value. """
        return bool(abs((timeA - timeB).total_seconds()) >= 86400*dayDelta)

#___________________________________________________________________________________________________ differsByHours
    @classmethod
    def differsByHours(cls, timeA, timeB, hourDelta):
        """ Computes the difference between the two datetime objects and returns a boolean, which
            is true if the absolute number of hours between the two datetimes is greater than or
            equal to the specified delta value. """
        return bool(abs((timeA - timeB).total_seconds()) >= 3600*hourDelta)

#___________________________________________________________________________________________________ differsBySeconds
    @classmethod
    def differsByMinutes(cls, timeA, timeB, minuteDelta):
        """ Computes the difference between the two datetime objects and returns a boolean, which
            is true if the absolute number of minutes between the two datetimes is greater than or
            equal to the specified delta value. """
        return bool(abs((timeA - timeB).total_seconds()) >= 60*minuteDelta)

#___________________________________________________________________________________________________ differsBySeconds
    @classmethod
    def differsBySeconds(cls, timeA, timeB, secondDelta):
        """ Computes the difference between the two datetime objects and returns a boolean, which
            is true if the absolute number of seconds between the two datetimes is greater than or
            equal to the specified delta value. """
        return bool(abs((timeA - timeB).total_seconds()) >= secondDelta)

#___________________________________________________________________________________________________ utcTodayAt
    @classmethod
    def utcTodayAt(cls, hour =0, minute =0, second =0, microsecond =0):
        """midnightToday doc..."""
        d = datetime.utcnow()
        return d.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)

#___________________________________________________________________________________________________ minutesSince
    @classmethod
    def minutesSince(cls, referenceTime, nowTime =None):
        """minutesSince doc..."""
        if nowTime is None:
            nowTime = datetime.utcnow()
        return float((nowTime - referenceTime).total_seconds())/60.0
