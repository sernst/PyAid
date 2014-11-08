# Route53Connection.py
# (C)2012-2013
# Scott Ernst and Eric D. Wills

from __future__ import print_function, absolute_import, unicode_literals, division

from boto.route53.connection import Route53Connection as BotoRoute53Connection

#___________________________________________________________________________________________________ Route53Connection
class Route53Connection(object):
    """Class for interacting with an Amazon Route53 DNS."""

#===================================================================================================
#                                                                                      C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, awsKey, awsSecret):
        """Creates a new instance of the Route53Connection class"""
        self._connection  = BotoRoute53Connection(awsKey, awsSecret)
        self._zones       = None
        self._namedZones  = dict()
        self._idZones     = dict()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: zones
    @property
    def zones(self):
        return self._zones

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ loadAllZones
    def loadAllZones(self):
        return self._connection.get_all_hosted_zones()

#___________________________________________________________________________________________________ getZoneByID
    def getZoneByID(self, zoneID):
        if self._zones:
            for z in self._zones:
                if z.id == zoneID:
                    self._idZones[zoneID] = z
                    return z

        z = self._connection.get_hosted_zone(zoneID)
        self._idZones[zoneID] = z

        return z

#___________________________________________________________________________________________________ getZoneByName
    def getZoneByName(self, name):
        if self._zones:
            for z in self._zones:
                if z.name == name:
                    self._namedZones[name] = z
                    return z

        z = self._connection.get_hosted_zone_by_name(name)
        self._namedZones[name] = z

        return z

#___________________________________________________________________________________________________ getRecordSet
    def getRecordSet(self, zone, recordType =None, name =None, recordID =None, limit =None):
        return self._connection.get_all_rrsets(
            hosted_zone_id=zone,
            type=recordType,
            name=name,
            identifier=recordID,
            maxitems=limit)

