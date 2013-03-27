# DatabaseError.py
# (C)2011
# Scott Ernst

#___________________________________________________________________________________________________ DatabaseError
class DatabaseError(Exception):
    """Represents exceptions related to DatabaseConnection activity."""

#___________________________________________________________________________________________________ __init__
    def __init__(self, message, info=None, command=None):
        self._command = command
        self._info    = info

        Exception.__init__(self, message)

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return 'DatabaseError\nCommand: %s\nInfo %s\n%s' % (
            str(self._command), str(self._info), Exception.__str__(self)
        )

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return 'DatabaseError\nCommand: %s\nInfo %s\n%s' % (
            unicode(self._command), unicode(self._info), Exception.__unicode__(self)
        )
