from enum import Enum
import abc

"""
State represent the state of the game
"""


class State(Enum):
    PLAYING = 1
    DRAW = 2
    CROSS_WON = 3
    CIRCLE_WON = 4


"""
Cell State represents the content of a cell, Empty, CROSS , CIRCLE, NULL when there is a DRAW in a mini board
"""


class CellState(Enum):
    EMPTY = 0
    CROSS = 1
    CIRCLE = 2
    NULL = 3


"""
ICell is an abstract class that represent a cell
This class is used as a part for the composite Pattern, since a Master board has mini boards which are cells
those mini boards also contains cells 

"""


class ICell(metaclass=abc.ABCMeta):
    def __init__(self):
        super(ICell, self).__init__()

    """
        get the the row of a cell
    """

    @abc.abstractmethod
    def get_row(self):
        pass

    """
        get the the col of a cell
    """

    @abc.abstractmethod
    def get_col(self):
        pass

    """
        get the content of a cell, or the player : i.e CROSS or CIRCLE , or NULL
    """

    @abc.abstractmethod
    def get_player(self):
        pass

    @abc.abstractmethod
    def set_player(self, player):
        pass

    """
        empty a cell
    """

    @abc.abstractmethod
    def clear(self):
        pass

    """
        returns what ever a cell is empty or not
    """

    @abc.abstractmethod
    def is_empty(self):
        pass


"""
IBoard is an abstract class that describe the main attributes and methods of a Board
a Board (what ever a Master or a Mini board) contains a matrix of cells 
the cells are either mini boards, or small cells 
"""


class IBoard(metaclass=abc.ABCMeta):
    def __init__(self):
        super(IBoard, self).__init__()
        self.cells = []
        self.current_row = 0
        self.current_col = 0

    @abc.abstractmethod
    def initialize(self):
        pass

    """
        returns true if there is a draw
    """

    def is_draw(self):
        for row in self.cells:
            for cell in row:
                if cell.is_empty():
                    return False
        return True

    """
        :param player
        :return true if player has won the game
    """

    def has_won(self, player):
        return (self.cells[self.current_row][0].get_player() == player  # 3 - in -the - row
                and self.cells[self.current_row][1].get_player() == player
                and self.cells[self.current_row][2].get_player() == player
                or self.cells[0][self.current_col].get_player() == player  # 3 - in -the - column
                and self.cells[1][self.current_col].get_player() == player
                and self.cells[2][self.current_col].get_player() == player
                or self.current_row == self.current_col  # 3 - in -the - diagonal
                and self.cells[0][0].get_player() == player
                and self.cells[1][1].get_player() == player
                and self.cells[2][2].get_player() == player
                or self.current_row + self.current_col == 2  # 3 - in -the - opposite - diagonal
                and self.cells[0][2].get_player() == player
                and self.cells[1][1].get_player() == player
                and self.cells[2][0].get_player() == player)


"""
a Cell contains a row and a col that represent its coordinates
and a player attribute to indicate who is occupying the cell
"""


class Cell(ICell):
    def __init__(self, row, col):
        super(Cell, self).__init__()
        self.row = row
        self.col = col
        self.player = CellState.EMPTY

    def __str__(self):
        return self.player.name

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def get_player(self):
        return self.player

    def set_player(self, player):
        self.player = player

    def clear(self):
        self.player = CellState.EMPTY

    def is_empty(self):
        return self.player == CellState.EMPTY


"""
the Board class is our Mini Board, it inherent the ICell class and the IBoard class 
the class define the abstract method initialize and init the self.cells attribute with  small cells
it also contains an attribute as_cell since this mini board is also represented as cell
the class define all the abstract methods of the ICell and IBoard classes

"""


class Board(ICell, IBoard):
    def __init__(self, row=0, col=0):
        super(Board, self).__init__()
        self.as_cell = Cell(row, col)
        self.initialize()

    """
        String representation of the Board 
    """

    def __str__(self):
        string = ""
        for row in self.cells:
            for cell in row:
                string = string + cell.__str__() + " "
            string += "\n"
        return string

    def get_row(self):
        return self.as_cell.get_row()

    def get_col(self):
        return self.as_cell.get_col()

    def get_player(self):
        return self.as_cell.get_player()

    def set_player(self, player):
        self.as_cell.set_player(player)

    def clear(self):
        for row in self.cells:
            for cell in row:
                cell.clear()

        self.as_cell.clear()

    def is_empty(self):
        return self.as_cell.is_empty()

    """
        fill the self.cells attribute of the IBoard class with Cell instances
    """

    def initialize(self):
        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append(Cell(i, j))
            self.cells.append(row)

    """
        set_cell method change the state of cell that described by the row and the col in this board
        than it updates the current_row and current_col
        the method calls the has won method of that player, if he won, then it changes the state of the board to the 
        player who won other wise, if there is a draw , this mini board state is NULL
    """

    def set_cell(self, row, col, player):
        if not self.as_cell.is_empty():
            return

        self.cells[row][col].set_player(player)  # set cell content
        self.current_row = row  # update current row
        self.current_col = col  # update col
        if self.has_won(player):  # if player won
            self.as_cell.set_player(player)  # set as_cell content to this player
        elif self.is_draw():  # if there is a draw
            self.as_cell.set_player(CellState.NULL)  # set the as_cell content to NULL


"""
The MasterBoard class contains mini boards, i.e cells of Board instances

"""


class MasterBoard(IBoard):
    def __init__(self):
        super(MasterBoard, self).__init__()
        self.initialize()

    def __str__(self):
        string = ""
        for i in range(3):
            for j in range(3):
                string += self.cells[i][j].get_player().__str__() + " "
            string += "\n"
        return string

    """
        initialize the cells attribute with Board instances
    """

    def initialize(self):
        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append(Board(i, j))
            self.cells.append(row)

    """
        this method is to set a cell is the mini board
        :param board_move: the coordinates of the mini board in the MasterBoard
        :param cell_move: the coordinates of the cell in the mini board
        
    """

    def set_cell_in_board(self, board_move, cell_move, player):
        i, j = board_move
        row, col = cell_move

        self.cells[i][j].set_cell(row, col, player)
        self.current_row = i
        self.current_col = j
        if self.has_won(player):  # if there is a winner, we return who won
            return State.CROSS_WON if player == CellState.CROSS else State.CIRCLE_WON
        elif self.is_draw():  # other wise, if there is a draw, we return Draw
            return State.DRAW
        # other wise the game continues
        return State.PLAYING
    """
        check if a mini board is taken or not, i.e either the mini board content is X or O or NULL
        :return true if the mini board is not empty, i
    """
    def is_taken(self, board):
        i, j = board
        return not self.cells[i][j].is_empty()
