# BlockDefinition.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.ArgsUtils import ArgsUtils
from pyaid.text.BlockSyntaxEnum import BlockSyntaxEnum
from pyaid.text.MatchLookDefinition import MatchLookDefinition

#___________________________________________________________________________________________________ BlockDefinition
class BlockDefinition(object):
    """A class for..."""

    BLOCKED = '~blocked'

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, name, pattern, blockType, terminator =None, **kwargs):
        """Creates a new instance of ClassTemplate."""
        self.name           = name
        self.pattern        = pattern
        self.blockType      = blockType
        self._terminator    = terminator
        self.findState      = ArgsUtils.get('findState', None, kwargs)
        self.matchReqs      = ArgsUtils.get('matchReqs', None, kwargs)
        self.terminatorReqs = ArgsUtils.get('terminatorReqs', None, kwargs)
        self.chainBlocks    = ArgsUtils.get('chainBlocks', False, kwargs)
        self.chainBreakers  = ArgsUtils.getAsList('chainBreakers', kwargs)
        self.closeAtEnd     = ArgsUtils.get('closeAtEnd', False, kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: terminator
    @property
    def terminator(self):
        return self.pattern if self._terminator is None else self._terminator

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addChainBreaker
    def addChainBreaker(self, breaker):
        if not isinstance(breaker, list):
            breaker = [breaker]

        for b in breaker:
            if b in self.chainBreakers:
                continue

            self.chainBreakers.append(b)

#___________________________________________________________________________________________________ createRegexDefinition
    @staticmethod
    def createDocTagDef(findState =None):
        return BlockDefinition(
            'DOCTAG', '@@@', BlockSyntaxEnum.DOC_TAG, '\n',
            matchReqs=MatchLookDefinition('[A-Za-z0-9_]+'),
            terminatorReqs=MatchLookDefinition('[\t\s]*(@@@[A-Za-z0-9_]+|$)'),
            findState=findState
        )

#___________________________________________________________________________________________________ createRegexDefinition
    @staticmethod
    def createRegexDef(findState =None):
        return BlockDefinition(
            'REGEX', '/', BlockSyntaxEnum.REGEX,
            matchReqs=MatchLookDefinition('[A-Za-z0-9_\)\]\}]{1}[\s\t\n]*'),
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createQuoteDefinition
    @staticmethod
    def createQuoteDef(findState =None):
        return BlockDefinition(
            'QUOTES', '"', BlockSyntaxEnum.STRING,
            matchReqs=MatchLookDefinition.createIgnoreEscapes(),
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createLiteralDefinition
    @staticmethod
    def createLiteralDef(findState =None, avoidApostrophes =False):
        return BlockDefinition(
            'LITERAL',
            re.compile('(?<![A-Za-z0-9])\'') if avoidApostrophes else '\'',
            BlockSyntaxEnum.STRING,
            re.compile('\'(?![A-Za-z0-9])') if avoidApostrophes else None,
            matchReqs=MatchLookDefinition.createIgnoreEscapes(),
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createTripleQuotesDefinition
    @staticmethod
    def createTripleQuotesDef(findState =None):
        return BlockDefinition(
            'TRIPLEQUOTES', '"""', BlockSyntaxEnum.STRING,
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createTripleQuotesDefinition
    @staticmethod
    def createTripleLiteralsDef(findState =None):
        return BlockDefinition(
            'TRIPLELITERALS', "'''", BlockSyntaxEnum.STRING,
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createTripleHashDefinition
    @staticmethod
    def createTripleHashDef(findState =None):
        return BlockDefinition('TRIPLEHASH', '###', BlockSyntaxEnum.COMMENT, findState=findState)

#___________________________________________________________________________________________________ createHashDefinition
    @staticmethod
    def createHashDef(findState =None):
        return BlockDefinition('HASH', '#', BlockSyntaxEnum.COMMENT, '\n', findState=findState)

#___________________________________________________________________________________________________ createSlashDefinition
    @staticmethod
    def createSlashDef(findState =None):
        return BlockDefinition(
            'SLASH', '//', BlockSyntaxEnum.COMMENT, '\n',
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createHashDefinition
    @staticmethod
    def createCStyleDef(findState =None):
        return BlockDefinition(
            'CSTYLE', '/*', BlockSyntaxEnum.COMMENT, '*/',
            matchReqs=MatchLookDefinition.createIgnoreEscapes(),
            terminatorReqs=MatchLookDefinition.createIgnoreEscapes(),
            findState=findState
        )

#___________________________________________________________________________________________________ createParensDef
    @staticmethod
    def createParensDef(findState =None):
        return BlockDefinition('PARENS', '(', BlockSyntaxEnum.PARENS, ')', findState=findState)

#___________________________________________________________________________________________________ createBracketsDef
    @staticmethod
    def createBracketsDef(findState =None):
        return BlockDefinition(
            'BRACKETS', '[', BlockSyntaxEnum.BRACKETS, ']', findState=findState
        )

#___________________________________________________________________________________________________ createBracesDef
    @staticmethod
    def createBracesDef(findState =None):
        return BlockDefinition('BRACKETS', '{', BlockSyntaxEnum.BRACES, '}', findState=findState)

#___________________________________________________________________________________________________ createVizmeMLCommentDef
    @staticmethod
    def createVizmeMLCommentDef(findState =None):
        return BlockDefinition(
            'VIZMEML_COMMENT', '[##]', BlockSyntaxEnum.COMMENT, '[/##]', findState=findState
        )

#___________________________________________________________________________________________________ createVizmeMLOpenDef
    @staticmethod
    def createVizmeMLOpenDef(findState =None):
        return BlockDefinition(
            'VIZMEML_OPEN', '[#', BlockSyntaxEnum.VIZMEML_OPEN, ']',
            matchReqs=MatchLookDefinition('[^A-Za-z_\]]+', lookAhead=True),
            terminatorReqs=MatchLookDefinition('\*'),
            findState=findState
        )

#___________________________________________________________________________________________________ createVizmeMLOpenDef
    @staticmethod
    def createVizmeMLCloseDef(findState =None):
        return BlockDefinition(
            'VIZMEML_CLOSE', '[/#', BlockSyntaxEnum.VIZMEML_CLOSE, ']',
            matchReqs=MatchLookDefinition('[^A-Za-z_\]]+', lookAhead=True),
            terminatorReqs=MatchLookDefinition('\*'),
            findState=findState
        )

#___________________________________________________________________________________________________ createVizmeMLOpenDef
    @staticmethod
    def createVizmeMLAttributeDef(findState =None):
        return BlockDefinition(
            'VIZMEML_ATTR',
            re.compile('(^|[\s\t\n]+)'),
            BlockSyntaxEnum.VIZMEML_ATTR,
            re.compile('($|[\s\t\n]+)'),
            matchReqs=MatchLookDefinition(',', True),
            terminatorReqs=MatchLookDefinition(',', True),
            findState=findState,
            chainBlocks=True,
            closeAtEnd=True
        )

#___________________________________________________________________________________________________ createCommaDelimitedListDef
    @staticmethod
    def createCommaDelimitedListDef(findState =None, startAtBeginning =False, continueToEnd =False):
        return BlockDefinition(
            'COMMA_LIST',
            re.compile('^|,') if startAtBeginning else ',',
            BlockSyntaxEnum.LIST_ITEM,
            re.compile('$|,') if continueToEnd else ',',
            closeAtEnd=continueToEnd,
            chainBlocks=True,
            findState=findState
        )
