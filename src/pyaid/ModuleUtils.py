# ModuleUtils.py
# (C)2014
# Scott Ernst

#___________________________________________________________________________________________________ ModuleUtils
class ModuleUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ importModule
    @classmethod
    def importModule(cls, package, globalVars, localVars, items =None):
            return __import__(package, globals(), locals(), items if items else [], -1)
