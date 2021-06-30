'''First program: MiniMaxOpening
The first program plays a move in the opening phase of the game. We request that you name it MiniMaxOpening.
For example, the input can be:
(you type:)
board1.txt board2.txt 2
(the program replies:)
Input position: xxxxxxxxxWxxxxxxBxxxx Output position: xxxxxxxxxWxxWxxxBxxxx
Positions evaluated by static estimation: 9.
MINIMAX estimate: 9987.
Here it is assumed that the file board1.txt exists and its content is:
xxxxxxxxxWxxxxxxBxxxx
The file board2.txt is created by the program, and its content is:
xxxxxxxxxWxxWxxxBxxxx
(The position and the numbers above may not be correct. They are given just to illustrate the format.)
Please use the move generator and the static estimation function for the opening phase. You are not asked
to verify that the position is, indeed, an opening position. You may also assume that this game never goes
into the midgame phase.'''

from MorrisBoard import Board
from Algorithms import *


def static_est(board, pos):
    return board.open_estimate_white(pos)


def successor(board, pos, d):
    if d % 2 == 0:
        return board.gen_add_4_white(pos)
    else:
        return board.gen_add_4_black(pos)


def move(startpos, depth):
    reset_count()
    board = Board()
    finalpos, score = maxmin(board, startpos, 0, depth, static_est, successor)
    print("Input position: {}, Output position: {}, Positions evaluated by static: {}, MINIMAX estimate: {}".format(startpos, finalpos, get_count(), score))
    return finalpos


if __name__ == "__main__":
    startpos, outp, depth = optargs(argv)
    write_output(move(startpos, depth), outp)