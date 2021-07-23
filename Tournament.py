import ABGame
import ABOpening
import MiniMaxGameBlack
import MiniMaxOpeningBlack
import MiniMaxGameImproved
import MiniMaxOpeningImproved
from MorrisBoard import Board
from Algorithms import *
import time


opening_evals = [MiniMaxOpeningImproved.static_est_white, MiniMaxOpeningImproved.static_est_black]
opening_successors = [ABOpening.successor, MiniMaxOpeningBlack.successor]
midend_evals = [MiniMaxGameImproved.static_est_white, MiniMaxGameImproved.static_est_black]
midend_successors = [ABGame.successor, MiniMaxGameBlack.successor]
player_names = ['white', 'black']


class Tournament2:
    def __init__(self, player="white", time_per_move=5):
        self.player = player
        self.tpm = time_per_move
        self.board = Board()
        if player == "white":
            self.move_count = 0
            self.player_id = 0
        else:
            self.move_count = 1
            self.player_id = 1

    def move(self, pos):
        if self.move_count < 14:
            maxd = 17 - self.move_count
        elif 14 <= self.move_count <= 17:
            maxd = 4
        else:
            maxd = 100000
        d = 2
        t0 = time.time()
        best_pos = pos
        best_score = -100000
        while time.time() - t0 < self.tpm and d < maxd:
            d += 1
            tmp, score = maxmin_ab_tourney(self.board, pos, 0, d, -100000, 100000, self.move_count, self.player_id)
            if score > best_score:
                best_score = score
                best_pos = tmp
        print("{} move {} {} {} {} {}".format(self.player, self.move_count, best_pos, best_score, d, time.time()-t0))
        self.move_count += 2
        if self.win(best_pos):
            print(self.player, "just won!")
        return best_pos

    def win(self, pos):
        if self.move_count < 18:
            return False
        if self.player == "white":
            return self.board.num_black_moves(pos) == 0
        return self.board.num_white_moves(pos) == 0


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
        best_pos = pos
        best_score = -100000
        while time.time() - t0 < self.tpm and d < 9 - n:
            d += 1
            tmp, score = maxmin_ab(self.board, pos, 0, d, static_est, successor, -100000, 100000, True)
            if score > best_score:
                best_score = score
                best_pos = tmp
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


def maxmin_ab_tourney(board, pos, curr_d, max_d, a, b, move, player):
    ply = move + curr_d
    #print("{}maxmin_ab {} {} {} {} {} {}".format("\t" * curr_d, pos, curr_d, max_d, ply, a, b))
    if ply <= 18:
        opening = True
        static_func = opening_evals[player % 2]
        gen_func = opening_successors[player % 2]
        if ply == 18:
            gen_func = midend_successors[player % 2]
    else:
        opening = False
        static_func = midend_evals[player % 2]
        gen_func = midend_successors[player % 2]
    #print("{}maxmin_ab {} {} {}.{} {}.{}".format("\t" * curr_d, ply, opening, static_func.__module__, static_func.__name__, gen_func.__module__, gen_func.__name__))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    max_score = -100000
    max_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = minmax_ab_tourney(board, child_pos, curr_d+1, max_d, a, b, move, player)
        if score > max_score:
            max_score = score
            max_pos = child_pos
        if max_score >= b:
            #print("{}beta cut {} {} {}".format("\t"*curr_d, b, max_score, max_pos))
            return max_pos, max_score
        else:
            a = max([max_score, a])
    #print("{}{} {}".format("\t"*curr_d, max_score, max_pos))
    return max_pos, max_score


def minmax_ab_tourney(board, pos, curr_d, max_d, a, b, move, player):
    ply = move + curr_d
    #print("{}minmax_ab {} {} {} {} {} {}".format("\t" * curr_d, pos, curr_d, max_d, ply, a, b))
    if ply <= 18:
        opening = True
        static_func = opening_evals[player % 2]
        gen_func = opening_successors[player % 2]
        if ply == 18:
            gen_func = midend_successors[player % 2]
    else:
        opening = False
        static_func = midend_evals[player % 2]
        gen_func = midend_successors[player % 2]
    #print("{}minmax_ab {} {} {}.{} {}.{}".format("\t" * curr_d, ply, opening, static_func.__module__, static_func.__name__, gen_func.__module__, gen_func.__name__))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    min_score = 100000
    min_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = maxmin_ab_tourney(board, child_pos, curr_d+1, max_d, a, b, move, player)
        if score < min_score:
            min_score = score
            min_pos = child_pos
        if min_score <= a:
            #print("{}alpha cut {} {} {}".format("\t"*curr_d, a, min_score, min_pos))
            return min_pos, min_score
        else:
            b = min([min_score, b])
    #print("{}{} {}".format("\t"*curr_d, min_score, min_pos))
    return min_pos, min_score


def end2end(time_per_move=2):
    c = 0
    pos = 'x' * 21
    white = Tournament("white", time_per_move)
    black = Tournament("black", time_per_move)

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


def end2end2(time_per_move=2):
    c = 0
    pos = 'x' * 21
    white = Tournament2("white", time_per_move)
    black = Tournament2("black", time_per_move)

    t0 = time.time()
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
    print(white.move_count, black.move_count, c, time.time() - t0)
