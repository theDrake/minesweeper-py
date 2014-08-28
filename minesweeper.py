#!/usr/bin/env python

#------------------------------------------------------------------------------
#    Filename: minesweeper.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: A simple Minesweeper game developed using Python 2.7.2 and PyGTK
#              2.24.0.
#------------------------------------------------------------------------------

import gtk
import pygtk
import random

SMALL             = 0
MEDIUM            = 1
LARGE             = 2
DEFAULT_SIZE      = SMALL
SIZE_DESCRIPTIONS = ["Small (10 x 10)",
                     "Medium (15 x 15)",
                     "Large (20 x 20)"]
ROW_COL_VALUES    = [(10, 10),
                     (15, 15),
                     (20, 20)]
CELL_SIZE         = 20   # Measured in pixels.
MINE_RATIO        = 0.10 # By default, ~10% of the cells will contain mines.
FLAG_IMAGE        = 'images/flag.jpg'
MINE_IMAGE        = 'images/mine.jpg'

#------------------------------------------------------------------------------
#       Class: Minesweeper
#
# Description: Manages a Minesweeper game.
#
#     Methods: __init__, createWindow, createMenu, addMenuItem, createTable,
#              run, deleteHandler, destroyHandler, resizeHandler,
#              restartHandler, restart, solveHandler, clickedHandler,
#              playerHasLost, playerHasWon, displayMessage
#------------------------------------------------------------------------------
class Minesweeper():
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Creates a window, vbox, menu, and table to serve as the
    #              Minesweeper GUI and manage game data.
    #
    #      Inputs: size - A value indicating the size of the game board.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, size):
        self.size = size
        (self.rows, self.cols) = ROW_COL_VALUES[self.size]
        self.createWindow(self.cols * CELL_SIZE, # width
                          self.rows * CELL_SIZE) # height
        self.createMenu()
        self.createTable(self.rows, self.cols)
        self.window.show_all()

    #--------------------------------------------------------------------------
    #      Method: createWindow
    #
    # Description: Creates a window (with vbox) to serve as the GUI.
    #
    #      Inputs: width  - Width of the window, in pixels.
    #              height - Height of the window, in pixels.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def createWindow(self, width, height):
        self.window = gtk.Window()
        self.window.set_default_size(width, height)
        self.window.set_resizable(False)
        self.window.set_title('Minesweeper')
        self.window.connect('destroy', self.destroyHandler)
        self.window.connect('delete_event', self.deleteHandler)
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)

    #--------------------------------------------------------------------------
    #      Method: createMenu
    #
    # Description: Creates a menu and adds it to the window's vbox.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def createMenu(self):
        self.menu = gtk.Menu()
        self.addMenuItem('New Game', self.restartHandler)
        self.addMenuItem('Resize', self.resizeHandler)
        self.addMenuItem('Solve', self.solveHandler)
        self.addMenuItem('Quit', self.destroyHandler)
        self.root_menu = gtk.MenuItem('Game')
        self.root_menu.set_submenu(self.menu)
        self.menubar = gtk.MenuBar()
        self.menubar.add(self.root_menu)
        self.vbox.add(self.menubar)

    #--------------------------------------------------------------------------
    #      Method: addMenuItem
    #
    # Description: Creates a menu item and adds it to the menu.
    #
    #      Inputs: title   - Title for the menu item.
    #              handler - Function to be called when the menu item is
    #                        selected.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def addMenuItem(self, title, handler):
        item = gtk.MenuItem(title)
        item.connect('activate', handler)
        self.menu.add(item)

    #--------------------------------------------------------------------------
    #      Method: createTable
    #
    # Description: Creates a table, complete with cells and buttons, to store
    #              and manage game board data.
    #
    #      Inputs: rows - Number of rows.
    #              cols - Number of columns.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def createTable(self, rows, cols):
        self.table = MinesweeperTable(rows, cols)
        for cell in self.table.getCells():
            cell.getButton().connect('button_release_event',
                                     self.clickedHandler)
        self.vbox.pack_start(self.table)

    #--------------------------------------------------------------------------
    #      Method: run
    #
    # Description: Runs the Minesweeper game via 'gtk.main()'.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def run(self):
        gtk.main()

    #--------------------------------------------------------------------------
    #      Method: deleteHandler
    #
    # Description: Handler for "delete" events. Ends the game.
    #
    #      Inputs: widget - The widget object that sent the signal (the window's
    #                       'X' button, in this case).
    #               event - The event object.
    #                data - Additional event data.
    #
    #     Outputs: Returns "False".
    #--------------------------------------------------------------------------
    def deleteHandler(self, widget, event, data=None):
        return False

    #--------------------------------------------------------------------------
    #      Method: destroyHandler
    #
    # Description: Handler for "destroy" signals. Ends the game.
    #
    #      Inputs: widget - The widget object that sent the signal (a menu item
    #                       or the window's 'X' button, in this case).
    #                data - Additional signal data.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def destroyHandler(self, widget, data=None):
        gtk.main_quit()

    #--------------------------------------------------------------------------
    #      Method: resizeHandler
    #
    # Description: Handler for "resize" signals. Allows the player to choose
    #              among three different size options. Starts a new game if a
    #              new size is selected.
    #
    #      Inputs: widget - The widget object that sent the signal (a menu item
    #                       in this case).
    #                data - Additional signal data.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def resizeHandler(self, widget, data=None):
        label = gtk.Label('Choose a new size:')
        dialog = gtk.Dialog('Resize',
          None,
          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
          (SIZE_DESCRIPTIONS[SMALL], SMALL,
                             SIZE_DESCRIPTIONS[MEDIUM], MEDIUM,
                             SIZE_DESCRIPTIONS[LARGE], LARGE,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        dialog.vbox.pack_start(label)
        label.show()
        response = dialog.run()
        dialog.destroy()
        if (response == SMALL or response == MEDIUM or response == LARGE) and \
           response != self.size:
            self.size = response
            (self.rows, self.cols) = ROW_COL_VALUES[self.size]
            self.restart()

    #--------------------------------------------------------------------------
    #      Method: restartHandler
    #
    # Description: Handler for "restart" signals. Starts a new game.
    #
    #      Inputs: widget - The widget object that sent the signal (a menu item
    #                       in this case).
    #                data - Additional signal data.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def restartHandler(self, widget, data=None):
        self.restart()

    #--------------------------------------------------------------------------
    #      Method: restart
    #
    # Description: Starts a new game by creating a new table.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def restart(self):
        self.vbox.remove(self.table)
        self.createTable(self.rows, self.cols)
        self.window.show_all()

    #--------------------------------------------------------------------------
    #      Method: solveHandler
    #
    # Description: Handler for "solve" signals. Removes all flags and hides all
    #              buttons to reveal the current game session's solution.
    #
    #      Inputs: widget - The widget object that sent the signal (a menu item
    #                       in this case).
    #                data - Additional signal data.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def solveHandler(self, widget, data=None):
        self.table.revealAllCells()

    #--------------------------------------------------------------------------
    #      Method: clickedHandler
    #
    # Description: Handler for "click" signals.
    #
    #      Inputs: widget - The widget object that sent the signal (a button in
    #                       this case).
    #                data - Additional signal data.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def clickedHandler(self, widget, data=None):
        if data.button == 1:    # Left-click.
            (row, col) = self.table.getRowColOfButton(widget)
            cell = self.table.getCells()[self.table.getIndex(row, col)]
            if self.playerHasLost(cell):
                self.restart()
                return
            else:
                self.table.revealCell(row, col)
        elif data.button == 3:  # Right-click.
            widget.toggleFlag()
        if self.playerHasWon():
            self.restart()

    #--------------------------------------------------------------------------
    #      Method: playerHasLost
    #
    # Description: Determines whether the player has lost the game. If so, a
    #              message is displayed.
    #
    #      Inputs: cell - The cell whose button was just left-clicked.
    #
    #     Outputs: Returns 'True' (and displays a dialog box) if the player has
    #              lost the game, otherwise returns 'False'.
    #--------------------------------------------------------------------------
    def playerHasLost(self, cell):
        if cell.containsMine():
            self.table.revealAllCells()
            self.displayMessage('Sorry, you landed on a mine. Try again!',
                                'Game over!')
            return True
        return False

    #--------------------------------------------------------------------------
    #      Method: playerHasWon
    #
    # Description: Determines whether the player has won the game. If so, a
    #              message is displayed.
    #
    #      Inputs: None.
    #
    #     Outputs: Returns 'True' (and displays a dialog box) if every non-mine
    #              cell has been revealed, otherwise returns 'False'.
    #--------------------------------------------------------------------------
    def playerHasWon(self):
        for cell in self.table.getCells():
            if not cell.containsMine() and not cell.isRevealed():
                return False
        self.displayMessage('Congratulations, you won!',
                            'Victory!')
        return True

    #--------------------------------------------------------------------------
    #      Method: displayMessage
    #
    # Description: Displays a message as a dialog box with an "OK" button.
    #
    #      Inputs: message - The string to display within the dialog box.
    #              title   - The string to display along the top of the dialog
    #                        box. (Optional.)
    #
    #     Outputs: None. However, a dialog box will appear.
    #--------------------------------------------------------------------------
    def displayMessage(self, message, title=""):
        label = gtk.Label(' ' + message + ' ')
        dialog = gtk.Dialog(title,
          None,
          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
          (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.vbox.pack_start(label)
        label.show()
        dialog.run()
        dialog.destroy()

#------------------------------------------------------------------------------
#       Class: MinesweeperTable
#
# Description: A table that constitutes the Minesweeper board, managing all its
#              cells and buttons.
#
#     Methods: __init__, placeMines, placeLabels, getCells,
#              getAdjacentMineCount, revealCell, revealAllCells, getIndex,
#              getRowCol, getRowColOfButton
#------------------------------------------------------------------------------
class MinesweeperTable(gtk.Table):
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Populates the MinesweeperTable with cells, buttons, mines,
    #              and labels for the non-mine cells surrounding each mine.
    #
    #      Inputs: rows        - Number of rows.
    #              cols        - Number of columns.
    #              mineRatio   - Ratio of mines vs. empty cells.
    #              homogeneous - If 'True', all table cells will be the same
    #                            size as the largest cell
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self,
                 rows,
                 cols,
                 mineRatio=MINE_RATIO,
                 homogeneous=True):
        gtk.Table.__init__(self, rows, cols, homogeneous)
        self.rows      = rows
        self.cols      = cols
        self.mineRatio = mineRatio
        self.cells     = []
        for row in range(rows):
            for col in range(cols):
                cell = MinesweeperCell()
                self.cells.append(cell)
                self.attach(cell.getButton(), col, col + 1, row, row + 1)
        self.placeMines()
        self.placeLabels()

    #--------------------------------------------------------------------------
    #      Method: placeMines
    #
    # Description: Places mines in randomly selected cells and attaches mine
    #              images to the table at corresponding locations.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def placeMines(self):
        mines = 0
        while mines < (self.rows * self.cols * self.mineRatio):
            row = random.randrange(0, self.rows)
            col = random.randrange(0, self.cols)
            i = self.getIndex(row, col)
            if not self.cells[i].containsMine():
                mines += 1
                self.cells[i].placeMine()
                self.attach(MinesweeperImage(MINE_IMAGE),
                            col,
                            col + 1,
                            row,
                            row + 1)

    #--------------------------------------------------------------------------
    #      Method: placeLabels
    #
    # Description: For each cell location on the board, if it has at least one
    #              mine next to it, the number of mines next to it is added to
    #              the table as a label.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def placeLabels(self):
        for row in range(self.rows):
            for col in range(self.cols):
                i = self.getIndex(row, col)
                if not self.cells[i].containsMine():
                    n = self.getAdjacentMineCount(row, col)
                    if n > 0:
                        self.cells[i].setAdjacentMines(n)
                        self.attach(gtk.Label(str(n)),
                                    col,
                                    col + 1,
                                    row,
                                    row + 1)

    #--------------------------------------------------------------------------
    #      Method: getCells
    #
    # Description: Provides access to the MinesweeperTable's list of cells.
    #
    #      Inputs: None.
    #
    #     Outputs: The cell list.
    #--------------------------------------------------------------------------
    def getCells(self):
        return self.cells

    #--------------------------------------------------------------------------
    #      Method: getAdjacentMineCount
    #
    # Description: Given a cell location, determines how many mines are
    #              adjacent to that cell (i.e., how many mine-containing cells
    #              share a side or corner with that cell) and returns that
    #              number.
    #
    #      Inputs: row - Row of the cell of interest.
    #              col - Column of the cell of interest.
    #
    #     Outputs: The number of mines surrounding the cell of interest.
    #--------------------------------------------------------------------------
    def getAdjacentMineCount(self, row, col):
        count = 0
        if self.cells[self.getIndex(row, col)].containsMine():
            return -1
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                    continue
                if self.cells[self.getIndex(r, c)].containsMine():
                    count += 1
        return count

    #--------------------------------------------------------------------------
    #      Method: revealCell
    #
    # Description: Recursive function that reveals the cell at a given location
    #              and, if it is empty (i.e., it bears neither mine nor label),
    #              also reveals all nearby cells that don't contain a mine.
    #
    #      Inputs: row - Row of the cell to reveal and analyze.
    #              col - Column of the cell to reveal and analyze.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def revealCell(self, row, col):
        i = self.getIndex(row, col)
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols or \
           self.cells[i].isRevealed() or self.cells[i].containsMine():
            return
        elif self.cells[i].getAdjacentMines() > 0:
            self.cells[i].reveal()
        else:
            self.cells[i].reveal()
            self.revealCell(row, col - 1)
            self.revealCell(row, col + 1)
            self.revealCell(row - 1, col)
            self.revealCell(row + 1, col)
            self.revealCell(row + 1, col - 1)
            self.revealCell(row + 1, col + 1)
            self.revealCell(row - 1, col - 1)
            self.revealCell(row - 1, col + 1)

    #--------------------------------------------------------------------------
    #      Method: revealAllCells
    #
    # Description: Reveals every cell (by hiding all buttons).
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def revealAllCells(self):
        for cell in self.cells:
            cell.reveal()

    #--------------------------------------------------------------------------
    #      Method: getIndex
    #
    # Description: Given the row and column of a cell, returns the appropriate
    #              index value for that cell (i.e., the index value for that
    #              cell within the MinesweeperTable's list of cells).
    #
    #      Inputs: row - Row of the cell of interest.
    #              col - Column of the cell of interest.
    #
    #     Outputs: The 'cells' list index value for the cell of interest.
    #--------------------------------------------------------------------------
    def getIndex(self, row, col):
        return (row * self.cols) + col

    #--------------------------------------------------------------------------
    #      Method: getRowCol
    #
    # Description: Given the cell list index value of a cell, returns the
    #              location (row and column) of that cell in tuple form.
    #
    #      Inputs: index - List index value of the cell of interest.
    #
    #     Outputs: A tuple containing first the row, then the column, of the
    #              cell of interest.
    #--------------------------------------------------------------------------
    def getRowCol(self, index):
        return (index / self.cols, index % self.cols)

    #--------------------------------------------------------------------------
    #      Method: getRowColOfButton
    #
    # Description: Given a MinesweeperButton object, returns the location (row
    #              and column) of that button in tuple form.
    #
    #      Inputs: button - The button object of interest.
    #
    #     Outputs: A tuple containing first the row, then the column, of the
    #              button of interest, or (-1, -1) if the button is not found.
    #--------------------------------------------------------------------------
    def getRowColOfButton(self, button):
        for i in range(self.rows * self.cols):
            if self.cells[i].getButton() == button:
                return self.getRowCol(i)
        return (-1, -1) # Indicates button was not found.

#------------------------------------------------------------------------------
#       Class: MinesweeperCell
#
# Description: Cells that make up the minesweeper board, some containing mines.
#
#     Methods: __init__, placeMine, containsMine, setAdjacentMines,
#              getAdjacentMines, reveal, isRevealed, getButton
#------------------------------------------------------------------------------
class MinesweeperCell:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Sets variables to default values and creates a button that
    #              will hide the MinesweeperCell.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self):
        self.mine          = False
        self.adjacentMines = 0
        self.button        = MinesweeperButton()

    #--------------------------------------------------------------------------
    #      Method: placeMine
    #
    # Description: Sets a variable to indicate that this cell contains a mine.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def placeMine(self):
        self.mine = True

    #--------------------------------------------------------------------------
    #      Method: containsMine
    #
    # Description: Determines whether this cell contains a mine.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if this cell contains a mine, otherwise 'False'.
    #--------------------------------------------------------------------------
    def containsMine(self):
        return self.mine

    #--------------------------------------------------------------------------
    #      Method: setAdjacentMines
    #
    # Description: Sets the value of a variable indicating the number of mine-
    #              containing cells that share a side or corner with this cell.
    #
    #      Inputs: num - The number of adjacent mines.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def setAdjacentMines(self, num):
        self.adjacentMines = num

    #--------------------------------------------------------------------------
    #      Method: getAdjacentMines
    #
    # Description: Returns a value indicating the number of mine-containing
    #              cells that share a side or corner with this cell.
    #
    #      Inputs: None.
    #
    #     Outputs: The number of adjacent mines.
    #--------------------------------------------------------------------------
    def getAdjacentMines(self):
        return self.adjacentMines

    #--------------------------------------------------------------------------
    #      Method: reveal
    #
    # Description: Reveals the cell by hiding its associated button.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def reveal(self):
        self.button.hide()

    #--------------------------------------------------------------------------
    #      Method: isRevealed
    #
    # Description: Determines whether this cell has been revealed.
    #
    #      Inputs: None.
    #
    #     Outputs: 'True' if this cell is currently visible, otherwise 'False'.
    #--------------------------------------------------------------------------
    def isRevealed(self):
        return (not self.button.get_visible())

    #--------------------------------------------------------------------------
    #      Method: getButton
    #
    # Description: Provides access to the cell's associated button.
    #
    #      Inputs: None.
    #
    #     Outputs: This cell's associated button object.
    #--------------------------------------------------------------------------
    def getButton(self):
        return self.button

#------------------------------------------------------------------------------
#       Class: MinesweeperButton
#
# Description: Buttons to cover cells, concealing mines. They can be flagged by
#              right-clicking or removed by left-clicking.
#
#     Methods: __init__, toggleFlag
#------------------------------------------------------------------------------
class MinesweeperButton(gtk.Button):
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the button and sets its width and height to the
    #              same preset value.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self):
        gtk.Button.__init__(self)
        self.set_size_request(CELL_SIZE, CELL_SIZE)

    #--------------------------------------------------------------------------
    #      Method: toggleFlag
    #
    # Description: Adds a flag image to the button, or removes the flag image
    #              if it was already present.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def toggleFlag(self):
        if self.get_image():
            if self.get_image().get_visible():
                self.get_image().set_visible(False)
            else:
                self.get_image().set_visible(True)
        else:
            self.set_image(MinesweeperImage(FLAG_IMAGE))

#------------------------------------------------------------------------------
#       Class: MinesweeperImage
#
# Description: Images scaled to fit within Minesweeper cells/buttons.
#
#     Methods: __init__
#------------------------------------------------------------------------------
class MinesweeperImage(gtk.Image):
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes a gtk.Image object based on a given filename,
    #              then scales the image to fit within a single cell/button.
    #
    #      Inputs: filename - Filename of the desired image.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, filename):
        gtk.Image.__init__(self)
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        pixbuf = pixbuf.scale_simple(CELL_SIZE - 1,
                                     CELL_SIZE - 1,
                                     gtk.gdk.INTERP_BILINEAR)
        self.set_from_pixbuf(pixbuf)

def main():
    game = Minesweeper(DEFAULT_SIZE)
    game.run()

if __name__ == '__main__':
    main()
