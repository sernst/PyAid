# CannedAclPolicyEnum.py
# (C) 2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

class CannedAclPolicyEnum(object):

#===================================================================================================
#                                                                                       C L A S S

    Private           = 'private'

    PublicRead        = 'public-read'

    PublicEdit        = 'public-read-write'

    # Owner gets FULL_CONTROL and any principal authenticated as a registered Amazon S3 user
    # is granted READ access
    AuthenticatedRead = 'authenticated-read'
