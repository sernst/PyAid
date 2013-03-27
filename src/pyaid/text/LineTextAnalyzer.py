# LineTextAnalyzer.py
# (C)2012
# Scott Ernst

from pyaid.text.LineMetadata import LineMetadata
from pyaid.text.RedactionTextAnalyzer import RedactionTextAnalyzer

#___________________________________________________________________________________________________ LineTextAnalyzer
class LineTextAnalyzer(RedactionTextAnalyzer):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, src ='', debug =False, blockDefs =None):
        """Creates a new instance of ClassTemplate."""
        RedactionTextAnalyzer.__init__(self, src, debug, blockDefs)

        self._lines        = []
        self._lineCursor   = 0
        self._startIndices = None
        self.refreshStartIndices()
        if debug:
            print 'START INDICES:', self._startIndices

        prev = None
        while True:
            line = LineMetadata(self, prev)
            if prev:
                prev.nextLine = line

            prev = line
            self._lines.append(line)

            if debug:
                print 'LINE: ',line.startIndex,line.endIndex,'of',len(self._raw)

            if not line.endIndex < len(self._raw) - 1:
                break

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: index
    @property
    def index(self):
        return self._lineCursor
    @index.setter
    def index(self, value):
        self._lineCursor = max(0, min(value, len(self._lines) - 1))

#___________________________________________________________________________________________________ GS: lineStartIndices
    @property
    def lineStartIndices(self):
        return self._startIndices
    @lineStartIndices.setter
    def lineStartIndices(self, value):
        self._startIndices = value

#___________________________________________________________________________________________________ GS: previousLine
    @property
    def previousLine(self):
        if self._lineCursor == 0:
            return None

        return self._lines[self._lineCursor - 1]

#___________________________________________________________________________________________________ GS: nextLine
    @property
    def nextLine(self):
        if self._lineCursor < len(self._lines) + 1:
            return self._lines[self._lineCursor + 1]

        return None

#___________________________________________________________________________________________________ GS: line
    @property
    def line(self):
        return self._lines[self._lineCursor]

#___________________________________________________________________________________________________ GS: lines
    @property
    def lines(self):
        return self._lines

#___________________________________________________________________________________________________ GS: lineCount
    @property
    def lineCount(self):
        return len(self._lines)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ changeOffsets
    def changeOffsets(self, index, amount):
        RedactionTextAnalyzer.changeOffsets(self, index, amount)

        for l in self._lines:
            if l.contains(index):
                l.setDirty(True)
                break

        # Updates the lines, adding or removing them as needed.
        lastLine = self._lines[-1]

        # REMOVE LINES
        while lastLine.startIndex == len(self.source):
            lastLine.destroy()
            lastLine = self._lines[-1]

        # ADD LINES
        while lastLine.endIndex < len(self.source):
            l                 = LineMetadata(self, lastLine)
            lastLine.nextLine = l
            lastLine          = l

#___________________________________________________________________________________________________ __iter__
    def __iter__(self):
        return self

#___________________________________________________________________________________________________ next
    def next(self):
        if self._lineCursor < len(self._lines):
            res = self._lines[self._lineCursor]
            self._lineCursor += 1
            return res

        self._lineCursor = 0
        raise StopIteration

#___________________________________________________________________________________________________ read
    def read(self, lineIndex =-1):
        if lineIndex != -1:
            return self._lines[max(0, min(lineIndex, len(self._lines) - 1))]

        return self._lines[self._lineCursor]

#___________________________________________________________________________________________________ getLineAtIndex
    def getLineAtIndex(self, index):
        for l in self._lines:
            if l.contains(index):
                return l

        return None

#___________________________________________________________________________________________________ refreshStartIndices
    def refreshStartIndices(self):
        self._startIndices = [0]
        index = 0
        while True:
            index = self.source.find('\n', index + 1)
            if index == -1:
                return

            self._startIndices.append(min(index + 1, len(self.source) - 1))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _insertImpl
    def _insertImpl(self, start, end, value):
        add = value.count('\n') - self.source[start:end].count('\n')
        RedactionTextAnalyzer._insertImpl(self, start, end, value)

        if add == 0:
            return

        for l in self._lines:
            if l.contains(start):
                nl = l
                if add > 0:
                    for i in range(0, add):
                        nl = nl.addLineAfter()
                else:
                    for i in range(0, abs(add)):
                        l.removeLineAfter()
                break

