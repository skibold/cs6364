import ABGame
import ABOpening
import MiniMaxGameBlack
import MiniMaxOpeningBlack
import MiniMaxGameImproved
import MiniMaxOpeningImproved
from MorrisBoard import Board
from Algorithms import maxmin_ab
import time


class Tournament:
    def __init__(self, player="white", time_per_move=2):
        self.player = player
        self.tpm = time_per_move
        self.board = Board()

    def open(self, pos, n):
        if self.player == 'white':
            static_est = MiniMaxOpeningImproved.static_est_white
            successor = ABOpening.successor
        else:
            static_est = MiniMaxOpeningImproved.static_est_black
            #static_est = MiniMaxOpeningBlack.static_est
            successor = MiniMaxOpeningBlack.successor
        d = 0
        t0 = time.time()
        while time.time() - t0 < self.tpm and d < 9 - n:
            d += 1
            best_pos, score = maxmin_ab(self.board, pos, 0, d, static_est, successor, -100000, 100000, True)
        print("{} move {} {} {}".format(self.player, best_pos, score, d))
        return best_pos

    def move(self, pos):
        if self.player == 'white':
            static_est = MiniMaxGameImproved.static_est_white
            successor = ABGame.successor
        else:
            static_est = MiniMaxGameImproved.static_est_black
            #static_est = MiniMaxGameBlack.static_est
            successor = MiniMaxGameBlack.successor
        d = 0
        t0 = time.time()
        best_pos = pos
        best_score = -100000
        while time.time() - t0 < self.tpm:
            d += 1
            tmp, score = maxmin_ab(self.board, pos, 0, d, static_est, successor, -100000, 100000, False)
            if score > best_score:
                best_score = score
                best_pos = tmp
        print("{} move {} {} {}".format(self.player, best_pos, best_score, d))
        return best_pos

    def win(self, pos):
        if self.player == "white":
            return self.board.num_black_moves(pos) == 0
        return self.board.num_white_moves(pos) == 0


def end2end(time_per_move=2):
    c = 0
    pos = 'x' * 21
    white = Tournament("white", time_per_move)
    black = Tournament("black", 10*time_per_move)

    t0 = time.time()
    print("Opening phase {}".format(pos))
    for i in range(9):
        pos = white.open(pos, i)
        pos = black.open(pos, i)
        c += 2

    print("Game phase")
    white_move = True
    while True:
        if white.win(pos):
            print("Game over, white victory {}".format(pos))
            break
        if black.win(pos):
            print("Game over, black victory {}".format(pos))
            break
        if white_move:
            pos = white.move(pos)
        else:
            pos = black.move(pos)
        c += 1
        white_move = not white_move
    print(c, time.time() - t0)
