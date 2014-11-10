# ModuleUtils.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys

if sys.version > '3':
    import importlib
    reload = importlib.reload

#___________________________________________________________________________________________________ ModuleUtils
class ModuleUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ reloadModule
    @classmethod
    def reloadModule(cls, target):
        """reloadModule doc..."""
        reload(target)

#___________________________________________________________________________________________________ importModule
    @classmethod
    def importModule(cls, package, globalVars, localVars, items =None):
            return __import__(package, globals(), locals(), items if items else [], -1)
