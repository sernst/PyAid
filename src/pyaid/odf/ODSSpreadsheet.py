# ODSSpreadsheet.py
# (C) 2010
# Thomas Gilray and Scott Ernst

import os
import shutil
from time import time

from odf.opendocument import load
from odf.table import Table, TableRow,TableCell
from odf.text import P

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ ODSSpreadsheet
class ODSSpreadsheet(object):
    """A class for more easily dealing with ODS files."""

#===================================================================================================
#                                                                                       C L A S S


#___________________________________________________________________________________________________ __init__
    def __init__(self, filepath, backuppath=""):
        """ Initializes private data.
            @param filepath: The path to an ODS file.
            @type filepath: string
            @param backuppath: [optional] The path to your backup folder.
            @type backuppath: string
        """

        self._doc        = 0
        self._time       = 0
        self._filepath   = filepath
        self._backuppath = backuppath
        if self._backuppath[-1:] != '/':
            self._backuppath += '/'

        self._time = str(int(time()))
        self.openSpreadsheet()

#___________________________________________________________________________________________________ openSpreadsheet
    def openSpreadsheet(self):
        """(Re)Loads the spreadsheet."""
        self._doc = load(self._filepath)

        rows      = self._doc.spreadsheet.getElementsByType(TableRow)
        dataWidth = 1

        # Determine data-width (as opposed to trailing blank cells)
        cells = rows[0].getElementsByType(TableCell)
        for cell in cells[1:]:
            pl = cell.getElementsByType(P)
            if len(pl) > 0 and (pl[0].firstChild) and len(StringUtils.toUnicode(pl[0].firstChild)) > 0:
                dataWidth += 1
            else:
                break

        # Expand out / decompress repeated cells (e.g. number-columns-repeated="2")
        for row in rows:
            cells  = row.getElementsByType(TableCell)
            colNum = 0
            for cell in cells:
                if colNum < dataWidth:
                    repeated = int(cell.getAttribute('numbercolumnsrepeated') or 0)
                    pl = cell.getElementsByType(P)
                    if repeated > 1:
                        if len(pl) > 0 and pl[0].firstChild and len(StringUtils.toUnicode(pl[0].firstChild)) > 0:
                            for i in range(repeated):
                                c = TableCell()
                                p = P()
                                p.addText(StringUtils.toUnicode(pl[0].firstChild))
                                c.addElement(p)
                                row.insertBefore(c, cell)
                            row.removeChild(cell)
                        else:
                            for i in range(min(repeated, dataWidth-colNum)):
                                c = TableCell()
                                p = P()
                                p.addText(StringUtils.toUnicode(''))
                                c.addElement(p)
                                row.insertBefore(c, cell)
                            row.removeChild(cell)
                else:
                    row.removeChild(cell)
                colNum += 1

            # Add a constant 3 trailing columns
            for i in range(3):
                c = TableCell()
                p = P()
                p.addText(StringUtils.toUnicode(''))
                c.addElement(p)
                row.addElement(c)

#___________________________________________________________________________________________________ saveSpreadsheet
    def saveSpreadsheet(self, savepath=""):
        """Loads the translation tables spreadsheet.
        @param savepath: An alternate path to use for saving the ods.
        @type savepath: string
        """
        # default to over-writing
        if len(savepath) < 4:
            savepath = self._filepath

        # first save a backup
        if len(self._backuppath) > 0:
            if not os.path.exists(self._backuppath):
                os.makedirs(self._backuppath)
            shutil.copy(self._filepath, self._backuppath
                + 'localization.ods.' + 'backup' + self._time)

        self._doc.save(savepath)
        self._doc = 0

#___________________________________________________________________________________________________ getDoc
    def getDoc(self):
        """Returns direct access to the odfpy document."""
        return self._doc

#___________________________________________________________________________________________________ insertColumn
    def insertColumn(self, sheetname, columnname, columnnumber):
        """Inserts a new empty column into the current doc.
        @param sheetname: The name of the sheet to be added to.
        @type sheetname: string
        @param columnname: The name of the new column to be added
        @type columnname: string
        @param columnnumber: Where to insert the new column (= how many come before it?)
        @type columnnumber: int
        """
        sheets = self._doc.spreadsheet.getElementsByType(Table)
        for sheet in sheets:
            if sheet.getAttribute('name') == sheetname:
                rownum = 0
                rows   = sheet.getElementsByType(TableRow)
                for row in rows:
                    colNum = 0
                    cells  = row.getElementsByType(TableCell)
                    for cell in cells:
                        if colNum == columnnumber:
                            newCell = TableCell()
                            if rownum == 0:
                                p = P()
                                p.addText(StringUtils.toUnicode(columnname))
                                newCell.addElement(p)
                            else:
                                p = P()
                                p.addText(StringUtils.toUnicode(''))
                                newCell.addElement(p)
                            row.insertBefore(newCell, cell)
                        colNum += 1
                    rownum += 1

#___________________________________________________________________________________________________ moveColumn
    def moveColumn(self, sheetname, oldcolumn, newcolumn):
        """Replaces the column oldcolumn with newcolumn and deletes newcolumn.
        This function assumes: oldcolumn > newcolumn.
        @param sheetname: The name of the sheet to be operated on.
        @type sheetname: string
        @param oldcolumn: The column to move data from.
        @type oldcolumn: int
        @param newcolumn: The column to move data to.
        @type newcolumn: int
        """
        sheets = self._doc.spreadsheet.getElementsByType(Table)
        for sheet in sheets:
            if sheet.getAttribute('name') == sheetname:
                rows = sheet.getElementsByType(TableRow)
                for row in rows:
                    colNum = 0
                    cells  = row.getElementsByType(TableCell)
                    for cell in cells:
                        if colNum == newcolumn:
                            newcolumncell = cell
                            pl = cell.getElementsByType(P)
                            for p in pl:
                                cell.removeChild(p)
                        elif colNum == oldcolumn:
                            pl = cell.getElementsByType(P)
                            if len(pl) > 0:
                                p = P()
                                if pl[0].firstChild:
                                    p.addText(StringUtils.toUnicode(pl[0].firstChild))
                                newcolumncell.addElement(p)
                        colNum += 1

#___________________________________________________________________________________________________ clearColumn
    def clearColumn(self, sheetname, column):
        """Clears a column of all data.
        @param sheetname: The name of the sheet to be operated on.
        @type sheetname: string
        @param column: The column to clear.
        @type column: int
        """
        sheets = self._doc.spreadsheet.getElementsByType(Table)
        for sheet in sheets:
            if sheet.getAttribute('name') == sheetname:
                rows = sheet.getElementsByType(TableRow)
                for row in rows:
                    colNum = 0
                    cells  = row.getElementsByType(TableCell)
                    for cell in cells:
                        if colNum == column:
                            pl = cell.getElementsByType(P)
                            for p in pl:
                                cell.removeChild(p)
                            p = P()
                            p.addText(StringUtils.toUnicode(''))
                            cell.addElement(p)
                        colNum += 1

#___________________________________________________________________________________________________ eraseColumn
    def eraseColumn(self, sheetname, column):
        """Erases a column completely (e.g. a|b|c becomes a|c, not a| |c).
        @param sheetname: The name of the sheet to be operated on.
        @type sheetname: string
        @param column: The column to erase.
        @type column: int
        """
        sheets = self._doc.spreadsheet.getElementsByType(Table)
        for sheet in sheets:
            if sheet.getAttribute('name') == sheetname:
                rows = sheet.getElementsByType(TableRow)
                for row in rows:
                    colNum = 0
                    cells  = row.getElementsByType(TableCell)
                    for cell in cells:
                        if colNum == column:
                            row.removeChild(cell)
                        colNum += 1

