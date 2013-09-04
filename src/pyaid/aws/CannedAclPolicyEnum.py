# CannedAclPolicyEnum.py
# (C) 2013
# Scott Ernst

class CannedAclPolicyEnum(object):

#===================================================================================================
#                                                                                       C L A S S

    Private           = 'private'

    PublicRead        = 'public-read'

    PublicEdit        = 'public-read-write'

    # Owner gets FULL_CONTROL and any principal authenticated as a registered Amazon S3 user
    # is granted READ access
    AuthenticatedRead = 'authenticated-read'
