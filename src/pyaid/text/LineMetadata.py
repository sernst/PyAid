# LineMetadata.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.text.BlockSyntaxEnum import BlockSyntaxEnum

#___________________________________________________________________________________________________ LineMetadata
class LineMetadata(object):
    """A class representing a line of text within the analyzed result of a LineTextAnalyzer. The
    LineMetadata provides functionality for parsing the analyzed results on a per line basis."""

#===================================================================================================
#                                                                                       C L A S S

    # Used to find the indentation for the line
    _INDENT_PATTERN = re.compile('^(?P<indent>[\s\t]*)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, analyzer, previousLine):
        """Creates a new instance of LineMetadata."""
        self._analyzer         = analyzer
        self._previousLine     = previousLine
        self._nextLine         = None

        self._blockChecked     = False
        self._inBlocks         = []
        self._overInBlocks     = []
        self._overOutBlocks    = []

        self._startIndex    = None
        self._endIndex      = None
        self._dead          = False

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: previousLine
    @property
    def previousLine(self):
        """The line appears before this line."""
        return self._previousLine
    @previousLine.setter
    def previousLine(self, value):
        self._previousLine = value

#___________________________________________________________________________________________________ GS: nextLine
    @property
    def nextLine(self):
        """The line that follows this line."""
        return self._nextLine
    @nextLine.setter
    def nextLine(self, value):
        self._nextLine = value

#___________________________________________________________________________________________________ GS: source
    @property
    def source(self):
        """The raw (unmodified) line of text that was provided to the analyzer."""
        return self._analyzer.source[self.startIndex:self.endIndex]

#___________________________________________________________________________________________________ GS: redacted
    @property
    def redacted(self):
        """The current redaction line returned by the analyzer and then modified by any explicit
        changes to the line."""
        if self._analyzer.redacted:
            return self._analyzer.redacted[self.startIndex:self.endIndex]
        else:
            return ''

#___________________________________________________________________________________________________ GS: lineNumber
    @property
    def lineNumber(self):
        """The 1-based index for the line. Used primarily for referencing the line for users."""
        return self.lineIndex + 1

#___________________________________________________________________________________________________ GS: lineIndex
    @property
    def lineIndex(self):
        """The 0-based index for the line as it is stored within the analyzer list."""
        if self.dead:
            return -1

        try:
            return self._analyzer.lines.index(self)
        except Exception:
            pass

        try:
            return 1 + self._analyzer.lines.index(self.previousLine)
        except Exception:
            pass

        try:
            return self._analyzer.lines.index(self.nextLine) - 1
        except Exception:
            pass

        return -1

#___________________________________________________________________________________________________ GS: startIndex
    @property
    def startIndex(self):
        """The character index at which the line begins."""
        if self.dead:
            return 0

        if not self._startIndex is None:
            return self._startIndex

        if self._analyzer.lineStartIndices is None:
            self._analyzer.refreshStartIndices()

        self._startIndex = self._analyzer.lineStartIndices[self.lineIndex]
        return self._startIndex

#___________________________________________________________________________________________________ GS: strippedStartIndex
    @property
    def strippedStartIndex(self):
        """The character index at which the indented line begins."""
        if self._dead:
            return 0

        return self.startIndex + self.indentLength

#___________________________________________________________________________________________________ GS: endIndex
    @property
    def endIndex(self):
        """The character index at which the line ends. This follows slicing notation, so the end
        index is not included in the line, the last character in the line is actually endIndex - 1
        so slicing of the full source text fullSource[line.startIndex:line.endIndex] will return
        the correct, complete line."""
        if self._dead:
            return 0

        if not self._endIndex is None:
            return self._endIndex

        end = self._analyzer.source.find('\n', self.startIndex)
        end = len(self._analyzer.source) if end == -1 else end + 1

        self._endIndex = end
        return self._endIndex

#___________________________________________________________________________________________________ GS: strippedEndIndex
    @property
    def strippedEndIndex(self):
        """The character index at which the line ends with whitespae and newlines stripped off the
        end. This follows slicing notation, so the end index is not included in the line."""
        if self._dead:
            return 0

        return self.endIndex - len(self.source) + len(self.source.rstrip())

#___________________________________________________________________________________________________ GS: indent
    @property
    def indent(self):
        """The whitespace indentation characters for the line."""
        res = LineMetadata._INDENT_PATTERN.search(self.source)
        return '' if res is None else res.group('indent')

#___________________________________________________________________________________________________ GS: indentLength
    @property
    def indentLength(self):
        """The character length of indentation for the line. Note, tab characters are counted as a
        single character. If you want the length of the line in terms of spaces, see the
        indentSpacesLength property."""
        return len(self.indent)

#___________________________________________________________________________________________________ GS: indentSpacesLength
    @property
    def indentSpacesLength(self):
        """The length of the indentation for the line in terms of number of spaces where tabs count
        as 4 spaces in compliance with indentation conventions."""
        return len(self.indent.replace('\t',4*' '))

#___________________________________________________________________________________________________ GS: isComment
    @property
    def isComment(self):
        """Specifies whether or not the line is entirely a comment. This is true when the line
        is part of a multi-line comment or is a line containing nothing but a comment."""
        for b in self._inBlocks:
            if b.blockType == BlockSyntaxEnum.COMMENT:
                return True

        return False

#___________________________________________________________________________________________________ GS: isString
    @property
    def isString(self):
        """Specifies whether or not the line is entirely a string. This is true when the line
        is part of a multi-line string or when the line contains nothing but a string."""
        for b in self._inBlocks:
            if b.blockType == BlockSyntaxEnum.STRING:
                return True

        return False

#___________________________________________________________________________________________________ GS: dead
    @property
    def dead(self):
        """Specifies whether or not the line has been set dead in which case it is no longer an
        active line in the analyzer result."""
        return self._dead

#___________________________________________________________________________________________________ GS: isEmpty
    @property
    def isEmpty(self):
        """Specifies whether or not the line is empty. Empty lines contain no characters or any
        number of whitespace and newline characters."""
        return len(self.redacted.strip()) == 0

#___________________________________________________________________________________________________ GS: blocks
    @property
    def blocks(self):
        """The block(s) that contains the line if such a block exists."""

        self.refreshBlocks()
        return self._inBlocks if len(self._inBlocks) > 0 else None

#___________________________________________________________________________________________________ GS: overlapInBlocks
    @property
    def overlapInBlocks(self):
        """The block(s) that overlap the line at the beginning if such a block exists."""

        self.refreshBlocks()
        return self._overInBlocks if len(self._overInBlocks) > 0 else None

#___________________________________________________________________________________________________ GS: overlapOutBlocks
    @property
    def overlapOutBlocks(self):
        """The block(s) that overlap the line at the end if such a block exists."""

        self.refreshBlocks()
        return self._overOutBlocks if len(self._overOutBlocks) > 0 else None

#___________________________________________________________________________________________________ GS: isEmpty
    @property
    def isSignificant(self):
        """Specifies whether or not the line contains significant text, i.e. text that is not part
        of a block (comment, string, or other depending on the blocks defined by the analyzer)."""

        self.refreshBlocks()
        return not self.isEmpty and not self.isComment and not self.isString

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ remove
    def remove(self):
        """Removes the line from the source by replacing it with an empty string. This causes this
        LineMetadata object to be destroyed; it will no longer be a valid member of the analyzer
        lines."""

        return self._analyzer.insertCharacters(self.startIndex, self.endIndex, '')

#___________________________________________________________________________________________________ destroy
    def destroy(self):
        """Destroys the line by removing it from the analyzer, extracting it from the previous
        and next line chain. The destruction preserves the line chain by connecting the destroyed
        lines previousLine and nextLines together."""

        if self._previousLine:
            self._previousLine.nextLine = self._nextLine

        if self._nextLine:
            self._nextLine.previousLine = self.previousLine

        self._dead         = True
        self._previousLine = None
        self._nextLine     = None
        self.setDirty()

        self._analyzer.lines.remove(self)

#___________________________________________________________________________________________________ setDirty
    def setDirty(self, propagate =False):
        """Marks the line dirty, which clears all forces the regeneration of all transient
        properties, which is necessary whenever the Analyzer's source text is modified.

        @@@param propagate:bool
            If true every line that follows this line will also be marked dirty.
        """

        self._analyzer.lineStartIndices = None
        self._endIndex      = None
        self._startIndex    = None

        self._blockChecked  = False
        self._inBlocks      = []
        self._overInBlocks  = []
        self._overOutBlocks = []

        if not propagate:
            return

        l = self.nextLine
        while l:
            l.setDirty()
            l = l.nextLine

#___________________________________________________________________________________________________ startsWithStripped
    def startsWithStripped(self, search, stripChars =None, redacted =False, regex =False):
        """Determines whether or not the line starts with the specified search characters or
        regular expression after the line is stripped. Useful when you want to ignore whitespace
        when checking the line for its starting characters.

        @@@param search:string
            The string or regular expression string to search for as the match. If the regular
            expression string does not include a ^ caret to force the match against the beginning
            of the line, it is automatically appended before conducting the search.

        @@@param stripChars:string -default='\\n\\t\\s'
            A string of characters to include in the stripping process. By default these are the
            whitespace and newline characters.

        @@@param redacted:boolean
            If true the search will take place on the redacted line instead of the raw line.

        @@@param regex:boolean
            If true the search will be a regular expression search instead of a simple string
            search.

        @@@return boolean
            Whether or not the line begins with the specified search string or regular expression.
        """

        s = (self.redacted if redacted else self.source).strip(stripChars)
        if regex:
            index = search.find('^')
            if index == -1 or (index > 0 and search[index-1] == '\\') or index > search.find('['):
                search = '^' + search
            p = re.compile(search)
            return p.search(s) is not None

        return s.startswith(search)

#___________________________________________________________________________________________________ endsWithStripped
    def endsWithStripped(self, search, stripChars =None, redacted =False, regex =False):
        """Determines whether or not the line ends with the specified search characters or
        regular expression after the line is stripped. Useful when you want to ignore whitespace
        when checking the line for its end characters.

        @@@param search:string
            The string or regular expression string to search for as the match. If the regular
            expression string does not include a $ character to force the match against the end
            of the line, it is automatically appended before conducting the search.

        @@@param stripChars:string -default='\n\t\s'
            A string of characters to include in the stripping process. By default these are the
            whitespace and newline characters.

        @@@param redacted:boolean
            If true the search will take place on the redacted line instead of the raw line.

        @@@param regex:boolean
            If true the search will be a regular expression search instead of a simple string
            search.

        @@@return boolean
            Whether or not the line ends with the specified search string or regular expression.
        """

        s = (self.redacted if redacted else self.source).strip(stripChars)

        if regex:
            index = search.find('$')
            if index == -1 or (index > 0 and search[index-1] == '\\') or index < search.find(']'):
                search += '$'
            p = re.compile(search)
            return p.search(s) is not None

        return s.endswith(search)

#___________________________________________________________________________________________________ contains
    def contains(self, index):
        """Determines whether or not the line contains the character index.

        @@@param index:int
            The index to check.

        @@@return bool
            Whether or not the index is contained within the line.
        """

        return self.startIndex <= index and (
            self.endIndex > index or self.endIndex == self.startIndex
        )

#___________________________________________________________________________________________________ containsRange
    def containsRange(self, start, end):
        """Determines whether or not the line contains the characters in the range start to end.

        @@@param start:int
            The starting index of the range to check.

        @@@param end:int
            The ending index of the range to check.

        @@@return bool
            Whether or not the range is fully contained within the line.
        """

        return self.startIndex <= start and self.endIndex >= end

#___________________________________________________________________________________________________ insert
    def insert(self, start, end, value):
        """Replaces the portion of the string from start to end with the specifed replacement.

        @@@param start:int
            The starting index at which the replace should occur.

        @@@param end:int
            The ending index at which the replace should occur. The end index is specifed in
            slicing format, so the end index is not included in the replace.

        @@@param replace:string
            The string that will be used as the replacement in the line.
        """

        self._analyzer.insertCharacters(self.startIndex + start, self.startIndex + end, value)

#___________________________________________________________________________________________________ overlapsStart
    def overlapsStart(self, indexes):
        """Determines if the specified index range overlaps the beginning of this line.

        @@@param indexes:list,tuple
            A two-length list or tuple representing the start and end index of the range to check.

        @@@return bool
            Whether or not the specified indexes range overlaps the beginning of the line.
        """

        return (indexes[0] < self.startIndex and indexes[1] > self.startIndex)

#___________________________________________________________________________________________________ overlapsEnd
    def overlapsEnd(self, indexes):
        """Determines if the specified index range overlaps the end of this line.

        @@@param indexes:list,tuple
            A two-length list or tuple representing the start and end index of the range to check.

        @@@return bool
            Whether or not the specified indexes range overlaps the end of the line.
        """

        return (indexes[0] < self.endIndex and indexes[1] > self.endIndex)

#___________________________________________________________________________________________________ overlaps
    def overlaps(self, indexes):
        """Determines if the specified index range overlaps either the beginning, end, or both of
        the line.

        @@@param indexes:list,tuple
            A two-length list or tuple representing the start and end index of the range to check.

        @@@return int
            Whether or not the specified indexes range overlaps the beginning/end or both of the
            line. If the range overlaps just the beginning or end, a value of 1 is returned, if
            it overlaps both 2 is returned, and if it overlaps none 0 is returned.
        """
        return self.overlapsStart(indexes) + self.overlapsEnd(indexes)

#___________________________________________________________________________________________________ refreshBlocks
    def refreshBlocks(self):
        """Used primarly by the analyzer class that owns this line, the checks through a list of
        blocks and finds the block that contains this line if such a block exists. If a block
        does exist it is stored in this line and the line properties are adjusted to account for
        the existance of the block.
        """
        if self._blockChecked:
            return

        for b in self._analyzer.blocks:
            overStart = b.start <= self.strippedStartIndex and b.end > self.strippedStartIndex
            overEnd   = b.start < self.strippedEndIndex and b.end >= self.strippedEndIndex

            if overStart and overEnd:
                self._isComment = b.blockType == BlockSyntaxEnum.COMMENT
                self._isString  = b.blockType == BlockSyntaxEnum.STRING
                self._inBlocks.append(b)
            elif overStart and b.start < self.strippedStartIndex:
                self._overInBlocks.append(b)
            elif overEnd and b.end > self.strippedEndIndex:
                self._overOutBlocks.append(b)

        self._blockChecked = True

#___________________________________________________________________________________________________ addLineAfter
    def addLineBefore(self):
        """Adds a new line to the line chain at the index prior to this line. This new line becomes
        the previousLine for this line."""

        pl                = LineMetadata(self._analyzer, self)
        pl.previousLine   = self.previousLine
        self.previousLine = pl

        l = pl
        while l:
            l.setDirty()
            l = l.nextLine

        self._analyzer.lines.insert(pl.lineIndex, pl)
        return pl

#___________________________________________________________________________________________________ addLineAfter
    def addLineAfter(self):
        """Adds a new line to the line chain after this line. This new line becomes the nextLine
        for this line."""

        nl            = LineMetadata(self._analyzer, self)
        nl.nextLine   = self.nextLine
        self.nextLine = nl

        l = self
        while l:
            l.setDirty()
            l = l.nextLine

        self._analyzer.lines.insert(nl.lineIndex, nl)
        return nl

#___________________________________________________________________________________________________ removeLineBefore
    def removeLineBefore(self):
        """Destroys  the line before this line from the line chain and reconnects the adjacent lines
        to preserve the modified line chain."""

        dead = self.previousLine
        dead.destroy()
        return dead

#___________________________________________________________________________________________________ removeLineAfter
    def removeLineAfter(self):
        """Destroys the line after this line from the line chain and reconnects the adjacent lines
        to preserve the modified line chain."""

        dead = self.nextLine
        dead.destroy()
        return dead
