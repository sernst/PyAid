# TextAnalyzer.py
# (C)2012-2013
# Scott Ernst

import re

from pyaid.ArgsUtils import ArgsUtils
from pyaid.debug.Logger import Logger
from pyaid.text.BlockDefinition import BlockDefinition
from pyaid.text.BlockSyntaxEnum import BlockSyntaxEnum
from pyaid.text.TextBlock import TextBlock
from pyaid.text.TextBookmark import TextBookmark

#___________________________________________________________________________________________________ TextAnalyzer
class TextAnalyzer(object):
    """Analyzes and potentially processes (via subclasses or explicit public processing) input
    text."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, src ='', debug =False, blockDefs =None, debugData =None, **kwargs):
        """Creates a new instance of ClassTemplate."""
        self._log = ArgsUtils.getLogger(self, kwargs)

        self._debugData = debugData
        self._debug     = debug

        if not isinstance(src, unicode):
            src = src.decode('utf8', 'ignore')

        self._raw = src.replace(u'\r',u'')
        if ArgsUtils.get('stripSource', True, kwargs):
            self._raw = self._raw.strip(u'\n')

        self._analyzed  = False
        self._errors    = []
        self._blocks    = []
        self._bookmarks = []
        self._initialBlock = ArgsUtils.get('initialBlock', None, kwargs)

        if isinstance(blockDefs, BlockDefinition):
            self._blockDefs = {'root':blockDefs}
        elif isinstance(blockDefs, dict):
            self._blockDefs = blockDefs
        elif isinstance(blockDefs, list):
            self._blockDefs = {'root':blockDefs}
        else:
            self._blockDefs = {
                'root':[
                    BlockDefinition.createQuoteDef(BlockDefinition.BLOCKED),
                    BlockDefinition.createLiteralDef(BlockDefinition.BLOCKED),
                    BlockDefinition.createParensDef(),
                    BlockDefinition.createBracketsDef(),
                    BlockDefinition.createBracesDef(),
                    ],
                }

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: debugData
    @property
    def debugData(self):
        """Logger instance for the processor."""
        return self._debugData

#___________________________________________________________________________________________________ GS: log
    @property
    def log(self):
        """Logger instance for the processor."""
        return self._log

#___________________________________________________________________________________________________ GS: source
    @property
    def source(self):
        return self._raw

#___________________________________________________________________________________________________ GS: analyzed
    @property
    def analyzed(self):
        return self._analyzed

#___________________________________________________________________________________________________ GS: syntaxErrors
    @property
    def syntaxErrors(self):
        return self._errors

#___________________________________________________________________________________________________ GS: bookmarks
    @property
    def bookmarks(self):
        return self._bookmarks

#___________________________________________________________________________________________________ GS: blocks
    @property
    def blocks(self):
        return self._blocks

#___________________________________________________________________________________________________ GS: parensBlocks
    @property
    def parensBlocks(self):
        res = []
        for b in self.blocks:
            if b.blockType == BlockSyntaxEnum.PARENS:
                res.append(b)
        return res

#___________________________________________________________________________________________________ GS: bracketBlocks
    @property
    def bracketBlocks(self):
        res = []
        for b in self.blocks:
            if b.blockType == BlockSyntaxEnum.BRACKETS:
                res.append(b)
        return res

#___________________________________________________________________________________________________ GS: bracesBlocks
    @property
    def bracesBlocks(self):
        res = []
        for b in self.blocks:
            if b.blockType == BlockSyntaxEnum.BRACES:
                res.append(b)
        return res

#___________________________________________________________________________________________________ GS: commentBlocks
    @property
    def commentBlocks(self):
        res = []
        for b in self.blocks:
            if b.blockType == BlockSyntaxEnum.COMMENT:
                res.append(b)
        return res

#___________________________________________________________________________________________________ GS: stringBlocks
    @property
    def stringBlocks(self):
        res = []
        for b in self.blocks:
            if b.blockType == BlockSyntaxEnum.STRING:
                res.append(b)
        return res

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ analyze
    def analyze(self, **kwargs):
        """Doc..."""

        self._analyzed = True
        self._preAnalyzeImpl()
        self._analyzeBlocks()
        self._postAnalyzeImpl()

#___________________________________________________________________________________________________ insertCharacters
    def insertCharacters(self, start, end, value, backCapPolicy =None, aheadCapPolicy =None):
        self._insertImpl(start, end, value)
        offset       = len(value) - end + start
        self.changeOffsets(start, offset)

        if aheadCapPolicy:
            aheadCapPolicy.modifyCap(self, end + offset)

        if backCapPolicy:
            backCapPolicy.modifyCap(self, start)

        return offset

#___________________________________________________________________________________________________ changeOffsets
    def changeOffsets(self, index, amount):
        for b in self._blocks + self._bookmarks:
            b.changeOffset(index, amount)

#___________________________________________________________________________________________________ indexInBlock
    def indexInBlock(self, index, blockTypes =None):
        if blockTypes and not isinstance(blockTypes, list):
            blockTypes = [blockTypes]

        for b in self._blocks:
            if (blockTypes is None or (blockTypes and b.blockType in blockTypes)) \
               and b.start <= index and b.end > index:
                return b

        return None

#___________________________________________________________________________________________________ lookAhead
    def lookAhead(self, index, pattern):
        return self._lookAhead(self._raw, index, pattern)

#___________________________________________________________________________________________________ lookBack
    def lookBack(self, index, pattern):
        return self._lookBack(self._raw, index, pattern)

#___________________________________________________________________________________________________ matches
    def matches(self, index, pattern, matchReqs =None):
        return self._matches(self._raw, index, pattern, matchReqs)

#___________________________________________________________________________________________________ findNearestBlock
    def findNearestBlock(self, index, blockTypes =None, contains =True, searchAhead =True,
                         searchBack =False):
        return self._findNearestBlock(index, self._blocks, blockTypes, contains, searchAhead,
                                      searchBack)

#___________________________________________________________________________________________________ addBookmark
    def addBookmark(self, start, end =None, name =None, data =None):
        newBook = TextBookmark(start, end, name, data)

        for b in self._bookmarks:
            if b.start > start:
                self._bookmarks.insert(self._bookmarks.index(b), newBook)
                return newBook

        self._bookmarks.append(newBook)
        return newBook

#___________________________________________________________________________________________________ getBookmark
    def getBookmark(self, name =None):
        for b in self._bookmarks:
            if b.name == name:
                return b

        return None

#___________________________________________________________________________________________________ createBlock
    def createBlock(self, start, end, blockDef):
        """Creates a new block and inserts it into the analyzers block list in the correct order,
        returning the newly created block for reference."""

        return self.insertBlock(TextBlock(blockDef, start, end))


#___________________________________________________________________________________________________ insertBlock
    def insertBlock(self, block, index =-1, afterBlock =None, beforeBlock =None):
        if afterBlock:
            try:
                self._blocks.insert(self._blocks.index(afterBlock) + 1, block)
            except Exception, err:
                pass
        elif beforeBlock:
            try:
                self._blocks.insert(self._blocks.index(beforeBlock) + 1, block)
            except Exception, err:
                pass

        if index != -1:
            self._blocks.insert(index, block)
            return

        index = 0
        for b in self._blocks:
            if b.start > block.start:
                self._blocks.insert(index, block)
                break
            elif b.start == block.start:
                if block.start == block.end or b.end < block.end:
                    self._blocks.insert(index, block)
                else:
                    self._blocks.insert(index + 1, block)
                break

            index += 1

        return block


#___________________________________________________________________________________________________ removeBookmark
    def removeBookmark(self, bookmark):
        self._bookmarks.remove(bookmark)
        return bookmark

#___________________________________________________________________________________________________ removeBookmarkByName
    def removeBookmarkByName(self, name):
        removes = []
        for b in self._bookmarks:
            if b.name == name:
                removes.append(b)

        for b in removes:
            self._bookmarks.remove(b)
        return removes

#___________________________________________________________________________________________________ getBlocksByType
    def getBlocksByType(self, blockType):
        res = []
        for b in self._blocks:
            if b.blockType == blockType:
                res.append(b)

        return res

#___________________________________________________________________________________________________ getBlocksByPattern
    def getBlocksByPattern(self, pattern):
        res = []
        for b in self._blocks:
            if b.pattern == pattern:
                res.append(b)

        return res

#___________________________________________________________________________________________________ getBlocksByPattern
    def getBlocksText(self, block):
        return self.source[block.start:block.end]

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyzeImpl
    def _preAnalyzeImpl(self):
        pass

#___________________________________________________________________________________________________ _postAnalyzeImpl
    def _postAnalyzeImpl(self):
        pass

#___________________________________________________________________________________________________ _insertImpl
    def _insertImpl(self, start, end, value):
        self._raw = self._raw[:start] + value + self._raw[end:]

#___________________________________________________________________________________________________ _findNearestBlock
    def _findNearestBlock(self, index, blocks, blockTypes =None, contains =True, searchAhead =True,
                          searchBack =False):
        if blockTypes and not isinstance(blockTypes, list):
            blockTypes = [blockTypes]

        res     = None
        prevSep = float('inf')
        for b in blocks:
            if (blockTypes is None or (blockTypes and b.blockType in blockTypes)):
                sep = b.distanceFromIndex(index, True, searchAhead, searchBack)
                if sep == 0:
                    return b

                if res is None:
                    res     = b
                    prevSep = sep
                    continue

                if sep < prevSep:
                    prevSep = sep
                    res     = b
                    continue

        return res

#___________________________________________________________________________________________________ _writeDebugLog
    def _writeDebugLog(self, *args, **kwargs):
        if self._debug:
            self._log(*args, **kwargs)

#___________________________________________________________________________________________________ _addBlock
    def _addBlock(self, start, end, blockDef):
        b = TextBlock(blockDef, start, end)
        self._blocks.append(b)
        return b

#___________________________________________________________________________________________________ _addError
    def _addError(self, message):
        self._errors.append({'message':message})

#___________________________________________________________________________________________________ _findTerminator
    def _findTerminator(self, src, index, pattern, matchReqs =None):
        index += len(pattern)
        if index >= len(src):
            return index

        stringPattern = isinstance(pattern, basestring)

        if stringPattern:
            endIndex = src.find(pattern, index)
            offset   = len(pattern)
        else:
            try:
                patternMatch = pattern.search(src, index)
                if patternMatch is None:
                    endIndex = -1
                else:
                    endIndex = patternMatch.start()
                    offset   = patternMatch.end() - patternMatch.start()
            except Exception, err:
                return index

        if endIndex == -1:
            self._writeDebugLog('TERMINATION ERROR!')
            self._addError('TERMINATION ERROR')
            endIndex = src.find('\n', index)
            return len(src) if endIndex == -1 else endIndex

        if matchReqs:
            if not isinstance(matchReqs, list):
                matchReqs = [matchReqs]

            for m in matchReqs:
                # Handles escape characters robustly with an iterative find instead of a
                # regular expression so that the number of escape characters can be counted
                # to prevent false positives on complex escape sequences.
                if m.escapeCharacter and self._isEscaped(src, endIndex, m.escapeCharacter):
                    return self._findTerminator(src, endIndex+1, pattern, matchReqs)

                if m.pattern:
                    if m.lookAhead:
                        res = self._lookAhead(src, endIndex, m.pattern)
                    else:
                        res = self._lookBack(src, endIndex, m.pattern)

                    if not res is None and res == m.ignoreIfFound:
                        return self._findTerminator(src, endIndex+1, pattern, matchReqs)

        return endIndex + offset

#___________________________________________________________________________________________________ _lookAhead
    def _isEscaped(self, src, index, escapeCharacter):
        count = 0
        while True:
            index -= 1
            if src[index] != '\\':
                break

            count += 1

        return count % 2

#___________________________________________________________________________________________________ _lookAhead
    def _lookAhead(self, src, index, pattern):
        if index > len(src) - 1:
            return None

        p = re.compile('^' + pattern)
        if p.search(src[index+1:]):
            return True

        return False

#___________________________________________________________________________________________________ _lookBack
    def _lookBack(self, src, index, pattern):
        if index == 0:
            return None

        p = re.compile(pattern + '$')
        if p.search(src[:index]):
            return True

        return False

#___________________________________________________________________________________________________ _matches
    def _matches(self, src, index, pattern, matchReqs =None):
        stringPattern = isinstance(pattern, basestring)

        if stringPattern:
            offset = len(pattern)
            if src[index:index+offset] != pattern:
                return False
        else:
            try:
                patternMatch = pattern.match(src, index)
                if patternMatch is None:
                    return False
                offset = patternMatch.end() - patternMatch.start()
            except Exception, err:
                return False

        # Check match requirements
        if not matchReqs:
            return True

        if not isinstance(matchReqs, list):
            matchReqs = [matchReqs]

        for m in matchReqs:
            # Handles escape characters robustly with an iterative find instead of a
            # regular expression so that the number of escape characters can be counted
            # to prevent false positives on complex escape sequences.
            if m.escapeCharacter and self._isEscaped(src, index, m.escapeCharacter):
                return False

            if m.pattern:
                if m.lookAhead:
                    res = self._lookAhead(src, index + offset - 1, m.pattern)
                else:
                    res = self._lookBack(src, index, m.pattern)

                if not res is None and res == m.ignoreIfFound:
                    return False

        return True

#___________________________________________________________________________________________________ _analyzeBlocks
    def _analyzeBlocks(self, blockTypes =None):
        if not self._blockDefs:
            return

        index    = 0
        s        = self._raw
        block    = self._addBlock(0, -1, self._initialBlock) if self._initialBlock else None
        findDefs = self._getFindBlockDefs(block) if block else self._blockDefs['root']

        while index < len(s):
            #---------------------------------------------------------------------------------------
            # IDENTIFY BLOCKS
            for d in findDefs:
                if self._matches(s, index, d.pattern, matchReqs=d.matchReqs):
                    # Handles the same block open twice at the start
                    if index == 0 and block and block.blockDef == d:
                        continue

                    if block and block.blockDef.chainBlocks and block.blockDef == d:
                        block.end = index + 1

                    self._addBlock(index, -1, d)
                    block    = self._blocks[-1]
                    findDefs = self._getFindBlockDefs(block)
                    break

                #-----------------------------------------------------------------------------------
                # CLOSE THE MATCHING OPEN BLOCK
                if block and block.blockDef == d \
                   and self._matches(s, index, d.terminator, matchReqs=d.terminatorReqs):
                    block.end = index + 1
                    block     = self._getNextOpenBlock()
                    findDefs  = self._getFindBlockDefs(block)
                    break

            #---------------------------------------------------------------------------------------
            # CLOSE "BLOCKED" BLOCKS
            if block and block.findState == BlockDefinition.BLOCKED:
                d          = block.blockDef
                index      = self._findTerminator(s, index, d.terminator, d.terminatorReqs)
                block.end  = index
                block      = self._getNextOpenBlock()
                findDefs   = self._getFindBlockDefs(block)
                continue

            index += 1

        # If the block should be closed by the last character, whether or not a terminator is found
        # set the end appropriately.
        for b in self._blocks:
            if b.blockDef.closeAtEnd and b.end == -1 or b.end == None:
                b.end = len(s)

#___________________________________________________________________________________________________ _getFindBlockDefs
    def _getFindBlockDefs(self, openBlock):
        if openBlock is None or openBlock.findState is None:
            return self._blockDefs['root']

        if openBlock.findState == BlockDefinition.BLOCKED:
            return []

        return self._blockDefs[openBlock.findState] + [openBlock.blockDef]

#___________________________________________________________________________________________________ _getNextOpenBlock
    def _getNextOpenBlock(self):
        for b in reversed(self._blocks):
            if b.end == -1 or b.end == None:
                return b
        return None


