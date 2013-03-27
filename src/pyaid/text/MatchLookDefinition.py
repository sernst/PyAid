# MatchLookDefinition.py
# (C)2012
# Scott Ernst

#___________________________________________________________________________________________________ MatchLookDefinition
class MatchLookDefinition(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, pattern, ignoreIfFound =True, lookAhead =False, escapeCharacter =None):
        """Creates a new instance of ClassTemplate."""

        self.pattern         = pattern
        self.ignoreIfFound   = ignoreIfFound
        self.lookAhead       = lookAhead
        self.escapeCharacter = escapeCharacter

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createRegexDefinition
    @staticmethod
    def createIgnoreEscapes():
        return MatchLookDefinition(None, True, False, '\\')
