from UltimateTicTacToeModel import MasterBoard, CellState, State
import random
import time

"""
    AIPlayer is an abstract class that wraps any strategy and stick it to the game using the method move
    the class take a MasterBoard, an which player to play
    the class also take a reference to the MasterBoard cells 
"""


class AIPlayer():
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

    def move(self):
        pass


class AIPlayerCorner(AIPlayer):
    def __init__(self, board, player):
        super(AIPlayerCorner, self).__init__(board, player)
        self.corner = [(2, 0), (0, 2), (0, 0)]
        self.rest = [(2, 2), (2, 1), (1, 2), (1, 1), (1, 0), (0, 1)]
        self.corner1 = [(2, 0), (0, 2), (0, 0)]
        self.rest1 = [(2, 2), (2, 1), (1, 2), (1, 1), (1, 0), (0, 1)]
        self.corner2 = [(2, 2), (0, 0), (0, 2)]
        self.rest2 = [(2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (0, 1)]
        self.corner3 = [(2, 0), (0, 2), (2, 2)]
        self.rest3 = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (1, 2)]
        self.corner4 = [(2, 2), (0, 0), (2, 0)]
        self.rest4 = [(1, 2), (0, 2), (0, 1), (1, 1), (2, 1), (1, 0)]
        self.player = player

    def move(self, board_move=None):
        if board_move is None:
            return
        if self.board.is_taken(board_move):
            self.choose_corner(board_move, self.board.cells)
            find = False
            for i in range(len(self.corner)):
                if not self.board.is_taken(self.corner[i]):
                    board_move = self.corner[i]
                    find = True
                    break
            if not find:
                for i in range(len(self.rest)):
                    if not self.board.is_taken(self.rest[i]):
                        board_move = self.rest[i]

        found = False
        self.choose_corner(board_move, self.board.cells[board_move[0]][board_move[1]].cells)
        for i in range(len(self.corner)):
            if self.board.cells[board_move[0]][board_move[1]].cells[self.corner[i][0]][self.corner[i][1]].is_empty():
                cell_move = self.corner[i]
                found = True
        if not found:
            for i in range(len(self.rest)):
                if self.board.cells[board_move[0]][board_move[1]].cells[self.rest[i][0]][self.rest[i][1]].is_empty():
                    cell_move = self.rest[i]
        return board_move, cell_move

    def choose_corner(self, board_move, cell):
        if not str(cell[2][2]) == str(self.player)[10:] or not cell[2][2].is_empty():
            self.corner = self.corner1
            self.rest = self.rest1
            return
        if not str(cell[2][0]) == str(self.player)[10:] or not cell[2][0].is_empty():
            self.corner = self.corner2
            self.rest = self.rest2
            return
        if not str(cell[0][0]) == str(self.player)[10:] or not cell[0][0].is_empty():
            self.corner = self.corner3
            self.rest = self.rest3
            return
        if not str(cell[0][2]) == str(self.player)[10:] or not cell[0][2].is_empty():
            self.corner = self.corner4
            self.rest = self.rest4
            return


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


class Node:
    def __init__(self, state=None, parent=None, children=None):
        self.state = BoardState() if state is None else state
        self.parent = parent
        self.children = [] if children is None else children

    def get_random_node(self):
        return self.children[random.randint(0, len(self.children) - 1)]

    def get_child_with_max_score(self):
        max_node = [-1, None]
        for child in self.children:
            if child.state.visit_count > max_node[0]:
                max_node = [child.state.visit_count, child]
        return max_node[1]


class Tree:
    def __init__(self):
        self.root = Node()

    def add_child(self, parent, child):
        parent.children.append(child)


import numpy as np


class UCT:
    @staticmethod
    def uct_value(total_visit, node_win_score, node_visit):
        if node_visit == 0:
            return float('inf')
        return (node_win_score * 1.0 / total_visit) + 1.41 * np.sqrt(np.log(total_visit) * 1.0 / node_visit)

    @staticmethod
    def find_best_node_uct(node):
        parent_visit = node.state.visit_count
        max_node = [-1, None]
        for child in node.children:
            uct = UCT.uct_value(parent_visit, child.state.win_score, child.state.visit_count)
            if uct > max_node[0]:
                max_node = [uct, child]
        return max_node[1]


import copy


class BoardState:
    def __init__(self, board=None, player=CellState.EMPTY, visit_count=0, win_score=0):
        self.board = MasterBoard() if board is None else board
        self.player = player
        self.visit_count = visit_count
        self.win_score = win_score

    def get_opponent(self):
        return CellState.CIRCLE if self.player == CellState.CROSS else CellState.CROSS

    def increment_visit(self):
        self.visit_count += 1

    def add_score(self, score):
        if self.win_score != -float("inf"):
            self.win_score += score

    def get_possible_states(self, board_move):
        states = []
        empty_cells = self.board.get_possible_moves(board_move)
        for b_move, c_move in empty_cells:
            state = BoardState(copy.deepcopy(self.board), self.get_opponent())
            state.board.set_cell_in_board(b_move, c_move, state.player)
            states.append(state)
        return states

    def random_play(self, board_move):
        empty_cells = self.board.get_possible_moves(board_move)
        b_move, c_move = empty_cells[random.randint(0, len(empty_cells) - 1)]
        self.board.set_cell_in_board(b_move, c_move, self.player)

    def toggle_player(self):
        self.player = CellState.CIRCLE if self.player == CellState.CROSS else CellState.CROSS


WIN_SCORE = 1000
import time


class MCTS:
    def __init__(self, level=3):
        self.level = level
        self.oponent = None
        self.board_move = None

    def get_millis_for_current_level(self):
        return 2 * (self.level - 1) + 1

    def find_next_move(self, board, player):
        start = int(round(time.time() * 1000))
        end = start + 60 * self.get_millis_for_current_level()
        self.oponent = CellState.CIRCLE if player == CellState.CROSS else CellState.CROSS
        tree = Tree()
        root = tree.root
        root.state.board = board
        root.state.player = self.oponent
        while int(round(time.time() * 1000)) < end:
            # selection
            promising_node = self.select_promising_node(root)
            # expansion
            if promising_node.state.board.check() == State.PLAYING:
                self.expand_node(promising_node)

            # simulation
            node_to_explore = promising_node
            if len(promising_node.children) > 0:
                node_to_explore = promising_node.get_random_node()

            playout_result = self.simulate_random_playout(node_to_explore)

            # update
            self.back_propogation(node_to_explore, playout_result)

        winner_node = root.get_child_with_max_score()
        tree.root = winner_node
        return winner_node.state.board

    def select_promising_node(self, root):
        node = root
        while len(node.children) != 0:
            node = UCT.find_best_node_uct(node)

        return node

    def expand_node(self, node):
        states = node.state.get_possible_states(self.board_move)
        for state in states:
            new_node = Node(state)
            new_node.parent = node
            new_node.state.player = node.state.get_opponent()
            node.children.append(new_node)

    def back_propogation(self, node, player):
        temp = node
        while temp is not None:
            temp.state.increment_visit()
            if temp.state.player == player:
                temp.state.add_score(WIN_SCORE)
            temp = temp.parent

    def simulate_random_playout(self, node):
        temp_node = copy.deepcopy(node)
        temp_state = temp_node.state
        status = temp_state.board.check()
        if status == self.oponent:
            temp_node.parent.state.win_score = -float("inf")
            return status
        while status == State.PLAYING:
            temp_state.toggle_player()
            temp_state.random_play(self.board_move)
            status = temp_state.board.check()
        return status


class AIPlayerMCTS(AIPlayer):
    def __init__(self, board, player):
        super(AIPlayerMCTS, self).__init__(board, player)
        self.mcts = MCTS()

    def move(self, board_move=None):
        self.mcts.board_move = board_move
        board = self.mcts.find_next_move(copy.deepcopy(self.board), self.player1)
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        if board.cells[i][j].cells[k][l].get_player() != self.board.cells[i][j].cells[k][l].get_player():
                            return (i, j), (k, l)
