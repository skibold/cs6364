'''Second program: MiniMaxGame
The second program plays in the midgame/endgame phase. We request that you call it MiniMaxGame.
For example, the input can be:
(you type:)
board3.txt board4.txt 3
(the program replies:)
Input position: xxxxxxxxxxWWxWWxBBBxx Output position: xxxxxxxxWWWxWWxBBBBxx.
Positions evaluated by static estimation: 125.
MINIMAX estimate: 9987.
Here it is assumed that the file board3.txt exists and its content is:
xxxxxxxxxxWWxWWxBBBxx
The file board4.txt is created by the program, and its content is:
xxxxxxxxWWWxWWxBBBBxx '''

from MorrisBoard import Board
from Algorithms import *


def static_est(board, pos):
    return board.mid_end_estimate_white(pos)


def successor(board, pos, d):
    if d % 2 == 0:
        if board.num_white(pos) == 3:
            return board.gen_hop_4_white(pos)
        else:
            return board.gen_move_4_white(pos)
    else:
        if board.num_black(pos) == 3:
            return board.gen_hop_4_black(pos)
        else:
            return board.gen_move_4_black(pos)


def move(startpos, depth):
    reset_count()
    board = Board()
    finalpos, score = maxmin(board, startpos, 0, depth, static_est, successor)
    print("Input position: {}, Output position: {}, Positions evaluated by static: {}, MINIMAX estimate: {}".format(startpos, finalpos, get_count(), score))
    return finalpos


if __name__ == "__main__":
    startpos, outp, depth = optargs(argv)
    write_output(move(startpos, depth), outp)
