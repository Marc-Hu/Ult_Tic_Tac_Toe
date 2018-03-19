from UltimateTicTacToeModel import *
import random
import time

"""
    AIPlayer is an abstract class that wraps any strategy and stick it to the game using the method move
    the class take a MasterBoard, an which player to play
    the class also take a reference to the MasterBoard cells 
"""


class AIPlayer(metaclass=abc.ABCMeta):
    def __init__(self, board, player):
        super(AIPlayer, self).__init__()
        self.board = board
        self.cells = board.cells
        self.player1 = None
        self.player2 = None
        self.set_ai_player(player)

    def set_ai_player(self, player):
        self.player1 = player  # ai player
        self.player2 = CellState.CIRCLE if player == CellState.CROSS else CellState.CROSS  # opponent

    @abc.abstractmethod
    def move(self):
        pass

class AIPlayerCorner(AIPlayer):
    def __init__(self, board, player):
        super(AIPlayerCorner, self).__init__(board, player)
        self.corner=[(0, 0), (0, 1), (0, 2)]
        self.rest=[(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        self.player=player

    def move(self, board_move=None):
        if board_move is None:
            return

        if self.board.is_taken(board_move):
            board_moves = []
            find=False
            for i in range(3):
                for j in range(3):
                    if not self.board.is_taken((i, j)):
                        if (i, j) in self.corner :
                            find=True
                            board_move=(i, j)
                            break
                        board_moves.append((i, j))
                if find :
                    break
            if not find :
                x=random.randint(0, len(self.rest)-1)
                board_moves=self.rest[x]
        found=False
        for i in range(len(self.corner)):
            if self.board.cells[board_move[0]][board_move[1]].cells[self.corner[i][0]][self.corner[i][1]].is_empty():
                cell_move=self.corner[i]
                found=True
        if not found:
            for i in range(len(self.rest)):
                if self.board.cells[board_move[0]][board_move[1]].cells[self.rest[i][0]][self.rest[i][1]].is_empty():
                    cell_move=self.rest[i]
        return board_move, cell_move



class AIPlayerRandom(AIPlayer):

    def __init__(self, board, player):
        super(AIPlayerRandom, self).__init__(board, player)

    def move(self, board_move=None):
        if board_move is None:
            return

        if self.board.is_taken(board_move):
            board_moves = []
            for i in range(3):
                for j in range(3):
                    if not self.board.is_taken((i, j)):
                        board_moves.append((i, j))

            x = random.randint(0, len(board_moves) - 1)

            board_move = board_moves[x]

        cell_moves = []
        for i in range(3):
            for j in range(3):
                if self.board.cells[board_move[0]][board_move[1]].cells[i][j].is_empty():
                    cell_moves.append((i, j))

        x = random.randint(0, len(cell_moves) - 1)

        cell_move = cell_moves[x]

        return board_move, cell_move


"""
AIPlayerMinimax is a minimax implementation of the MinMax algorithm
it's a sub class of the AIPlayer and define the move method
"""


class AIPlayerMinimax(AIPlayer):

    def __init__(self, board, player, depth=2):
        super(AIPlayerMinimax, self).__init__(board, player)  # call the super constructor
        self.depth = depth  # depth of minimax tree
        self.current_board_move = None  # which mini board we're playing on

    """
        move takes the current_board_move which represent the coordinates of the current mini board that's we playing on
        it updates the self.cells attribute, then it calls the minimax algorithm 
        :return list[board_move,cell_move]
    """

    def move(self, current_board_move=None):
        if current_board_move is not None:
            self.current_board_move = current_board_move

        self.cells = self.board.cells
        m = self.minimax(self.depth, self.player1, -float('inf'), float('inf'))
        return m[1:]

    """
        Minimax (recursive) at level of depth for maximizing or minimizing player
        with alpha-beta cut-off. Return int[3] of {score, board_move[], cell_move[]}  
    """

    def minimax(self, depth, player, alpha, beta):
        best_cell_move = [-1, -1]
        best_board_move = [-1, -1]
        #  Generate possible next moves in a list of int[2] of {row, col}.
        next_moves = self.generate_moves()

        # player1 is maximizing; while player2 is minimizing

        if len(next_moves) == 0 or depth == 0:
            # game over or depth reached, evaluate score
            score = self.evaluate()
            return [score, best_board_move, best_cell_move]
        else:
            for b_move, c_move in next_moves:
                # try a move
                i, j = b_move
                row, col = c_move
                self.board.set_cell_in_board(b_move, c_move, player)
                if player == self.player1:  # player1 (computer) is maximizing player
                    score = self.minimax(depth - 1, self.player2, alpha, beta)[0]
                    if score > alpha:
                        alpha = score
                        best_board_move = b_move
                        best_cell_move = c_move
                else:  # player2 is minimizing player
                    score = self.minimax(depth - 1, self.player1, alpha, beta)[0]
                    if score < beta:
                        beta = score
                        best_board_move = b_move
                        best_cell_move = c_move

                # undo move
                i, j = b_move
                k, l = c_move
                self.cells[i][j].cells[k][l].set_player(CellState.EMPTY)
                self.cells[i][j].set_player(CellState.EMPTY)
                # cut off
                if alpha >= beta:
                    break

        return [alpha if player == self.player1 else beta, best_board_move, best_cell_move]

    """
        generate_moves returns the possible moves
        there will be either 9 possible moves at most if the mini board is not taken 
        other wise there will be 64 moves at most 
        the method returns an empty list of moves if the one of the players has won the game 
        the returned value is a list of tuples (board_move,cell_move)
    """

    def generate_moves(self):
        next_moves = []
        # if a player has won the game, than we returns nothing
        if self.board.has_won(self.player1) or self.board.has_won(self.player2):
            return next_moves

        possible_board_moves = []
        # if the mini board is not empty
        if self.board.is_taken(self.current_board_move):
            # than we iterate though the cells of the master board (all the mini boards)
            for i in range(3):
                for j in range(3):
                    # if the mini board (i,j) is not taken, than we add it to the possible_board_moves
                    if not self.board.is_taken([i, j]):
                        possible_board_moves.append([i, j])
        else:
            # other wise we add just our current_board_move
            possible_board_moves.append(self.current_board_move)

        # for each mini board i,j
        for i, j in possible_board_moves:
            # for each cell row,col in the mini board
            for row in range(3):
                for col in range(3):
                    # if that cell is not empty thant we add a tuple ([i,j],[row,col]) to the next_moves list
                    if self.cells[i][j].cells[row][col].is_empty():
                        next_moves.append(([i, j], [row, col]))
        return next_moves

    """
        evaluate calculate the heuristic of the MasterBoard 
           The heuristic evaluation function for the given line of 3 cells
            +100, +10, +1 for 3-, 2-, 1-in-a-line for computer.
                   -100, -10, -1 for 3-, 2-, 1-in-a-line for opponent.
                   0 otherwise 
        we first calculate an heuristic of the mini boards 
        than we add to the the heuristic of cells of each mini board 
        
    """

    def evaluate(self):

        score = 0
        score += self.evaluate_line(self.cells, 0, 0, 0, 1, 0, 2)  # row 0
        score += self.evaluate_line(self.cells, 1, 0, 1, 1, 1, 2)  # row 1
        score += self.evaluate_line(self.cells, 2, 0, 2, 1, 2, 2)  # row 2
        score += self.evaluate_line(self.cells, 0, 0, 1, 0, 2, 0)  # col  0
        score += self.evaluate_line(self.cells, 0, 1, 1, 1, 2, 1)  # col 1
        score += self.evaluate_line(self.cells, 0, 2, 1, 2, 2, 2)  # col 2
        score += self.evaluate_line(self.cells, 0, 0, 1, 1, 2, 2)  # diagonal
        score += self.evaluate_line(self.cells, 0, 2, 1, 1, 2, 0)  # alternate diagonal
        score *= 10  # multiply the score by 10, since The MasterBoard is bigger 10 times than a mini board (optional)

        # for each mini board
        for row in self.cells:
            for mini_board in row:
                # calculate its heuristic
                score += self.evaluate_line(mini_board.cells, 0, 0, 0, 1, 0, 2)  # row 0
                score += self.evaluate_line(mini_board.cells, 1, 0, 1, 1, 1, 2)  # row 1
                score += self.evaluate_line(mini_board.cells, 2, 0, 2, 1, 2, 2)  # row 2
                score += self.evaluate_line(mini_board.cells, 0, 0, 1, 0, 2, 0)  # col  0
                score += self.evaluate_line(mini_board.cells, 0, 1, 1, 1, 2, 1)  # col 1
                score += self.evaluate_line(mini_board.cells, 0, 2, 1, 2, 2, 2)  # col 2
                score += self.evaluate_line(mini_board.cells, 0, 0, 1, 1, 2, 2)  # diagonal
                score += self.evaluate_line(mini_board.cells, 0, 2, 1, 1, 2, 0)  # alternate diagonal

        return score

    """
        The heuristic evaluation function for the given line of 3 cells
           Return +100, +10, +1 for 3-, 2-, 1-in-a-line for computer.
                   -100, -10, -1 for 3-, 2-, 1-in-a-line for opponent.
                   0 otherwise 
    """

    def evaluate_line(self, cells, r1, c1, r2, c2, r3, c3):
        score = 0
        cell1 = cells[r1][c1]
        cell2 = cells[r2][c2]
        cell3 = cells[r3][c3]

        if cell1.get_player() == self.player1:
            score = 1
        elif cell1.get_player() == self.player2:
            score = -1

        # cell2
        if cell2.get_player() == self.player1:
            if score == 1:
                score = 10
            elif score == -1:
                return 0
            else:
                score = 1
        elif cell2.get_player() == self.player2:
            if score == -1:
                score = -10
            elif score == 1:
                return 0
            else:
                score = -1
        # cell 3
        if cell3.get_player() == self.player1:
            if score > 0:
                score *= 10
            elif score < 0:
                return 0
            else:
                score = 1
        elif cell3.get_player() == self.player2:
            if score < 0:
                score *= 10
            elif score > 1:
                return 0
            else:
                score = -1

        return score
