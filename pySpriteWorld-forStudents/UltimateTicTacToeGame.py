from AI import AIPlayerMinimax, AIPlayerRandom, AIPlayerCorner, AIPlayerMCTS
from UltimateTicTacToeModel import MasterBoard, Board, CellState, State

"""
UTTTGame simulate two AIs playing against each other and define the rules of the game 

"""


class UTTTGame:
    def __init__(self):
        self.board = MasterBoard()  # MasterBoard
        self.current_player = None
        self.current_state = None  # state of the game, playing or draw or crossWIN,CircleWIN
        self.current_board_move = None  # to indicate which mini board we'll play next round
        self.cross = AIPlayerMinimax(self.board, CellState.CROSS)  # first AI plays cross
        self.circle = AIPlayerCorner(self.board, CellState.CIRCLE)  # second random player plays Cricle
        self.init_game()  # init game

    def play(self):
        # while self.current_state == State.PLAYING:

        # call cross.move or circle.move according the current_player value
        # i.e current_player == CROSS ? cross.move(): cricle.move()
        board_move, cell_move = self.cross.move(self.current_board_move) \
            if self.current_player == CellState.CROSS \
            else self.circle.move(self.current_board_move)
        # we call play a move to change the state of the board
        self.current_state = self.play_move(board_move, cell_move, self.current_player)
        # since the coordinates of cell_move defines the next mini board that we'll play on
        self.current_board_move = cell_move
        print(board_move, cell_move, self.current_player)
        # switch current player
        self.current_player = CellState.CIRCLE if self.current_player == CellState.CROSS else CellState.CROSS
        # if the state is not PLAYING, we print who is the winner or a draw if there is a draw
        if self.current_state != State.PLAYING:
            print("Winner = ", self.current_state)
        # return STATE,board_move,cell_move and STATE is True if we're still playing
        return self.current_state == State.PLAYING, board_move, cell_move

    def init_game(self):
        self.board.initialize()
        self.current_player = CellState.CIRCLE
        self.current_state = State.PLAYING
        self.current_board_move = [1, 1]

    # play move set a cell in a mini board
    def play_move(self, board_move, cell_move, player):
        return self.board.set_cell_in_board(board_move, cell_move, player)


if __name__ == '__main__':
    UTTTGame()
