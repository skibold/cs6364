'''Same as MiniMaxOpening, but for black'''

from MorrisBoard import Board
from Algorithms import *


def static_est(board, pos):
    return board.open_estimate_black(pos)


def successor(board, pos, d):
    if d % 2 == 1:
        return board.gen_add_4_white(pos)
    else:
        return board.gen_add_4_black(pos)


def move(startpos, depth):
    reset_count()
    board = Board()
    finalpos, score = maxmin(board, startpos, 0, depth, static_est, successor, True)
    print("Input position: {}, Output position: {}, Positions evaluated by static: {}, MINIMAX estimate: {}".format(startpos, finalpos, get_count(), score))
    return finalpos


if __name__ == "__main__":
    startpos, outp, depth = optargs(argv)
    write_output(move(startpos, depth), outp)