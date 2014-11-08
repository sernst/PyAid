# CoffeescriptAnalyzer.py
# (C)2012-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.text.BlockDefinition import BlockDefinition
from pyaid.text.BlockSyntaxEnum import BlockSyntaxEnum
from pyaid.text.LineTextAnalyzer import LineTextAnalyzer

#___________________________________________________________________________________________________ CoffeescriptAnalyzer
class CoffeescriptAnalyzer(LineTextAnalyzer):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _GLOBALS_PATTERN = re.compile('\n[\s\t]*#[\s\t]*(global|ignore)s?[\s\t]*(?P<globals>.+)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, src ='', debug =False):
        """Creates a new instance of ClassTemplate."""
        blocks = {'root':[
            BlockDefinition.createTripleHashDef(BlockDefinition.BLOCKED),
            BlockDefinition.createHashDef(BlockDefinition.BLOCKED),
            BlockDefinition.createRegexDef(BlockDefinition.BLOCKED),
            BlockDefinition.createTripleQuotesDef(BlockDefinition.BLOCKED),
            BlockDefinition.createTripleLiteralsDef(BlockDefinition.BLOCKED),
            BlockDefinition.createQuoteDef(BlockDefinition.BLOCKED),
            BlockDefinition.createLiteralDef(BlockDefinition.BLOCKED),
            BlockDefinition.createParensDef(),
            BlockDefinition.createBracketsDef(),
            BlockDefinition.createBracesDef() ]}

        LineTextAnalyzer.__init__(self, src, debug, blocks)
        self._globalClasses = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: globalObjects
    @property
    def globalObjects(self):
        return self._globalClasses

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyzeImpl
    def _preAnalyzeImpl(self):
        LineTextAnalyzer._preAnalyzeImpl(self)

        #-------------------------------------------------------------------------------------------
        # REGISTER GLOBAL CLASSES
        res = CoffeescriptAnalyzer._GLOBALS_PATTERN.finditer(self._raw)
        if res:
            for r in res:
                gs = r.group('globals').replace(' ','').replace('\t','').split(',')
                for g in gs:
                    if not g in self._globalClasses:
                        self._globalClasses.append(g)

#___________________________________________________________________________________________________ _redactBlockImpl
    def _redactBlockImpl(self, block, source, replace):
        replace = LineTextAnalyzer._redactBlockImpl(self, block, source, replace)

        #-----------------------------------------------------------------------------------
        # FIND STRING VARIABLES AND RETAIN THEM
        if block.blockType == BlockSyntaxEnum.STRING and '"' in block.pattern:
            variables = self._findCommentVariables(source)
            out       = replace
            for v in variables:
                out = out[:v[0]] + source[v[0]:v[1]] + out[v[1]:]
            return out

        return replace

#___________________________________________________________________________________________________ _findCommentVariables
    def _findCommentVariables(self, src):
        index        = 0
        variables    = []
        braceCount   = 0
        openVariable = None

        while index < len(src):
            if openVariable:
                if src[index] == '{':
                    braceCount += 1
                elif src[index] == '}' and braceCount > 0:
                    braceCount -= 1
                elif src[index] == '}' and braceCount == 0:
                    openVariable[1] = index
                    variables.append(openVariable)
                    openVariable = None
            elif src[index] == '#' and self._lookAhead(src, index, '{'):
                openVariable = [index + 2, -1]
                index += 2
                continue

            index += 1

        return variables

