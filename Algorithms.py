from sys import argv
from MorrisBoard import Board
import numpy as np


count = 0


def increment_count():
    global count
    count += 1


def reset_count():
    global count
    count = 0


def get_count():
    global count
    return count


def optargs(args):
    if len(args) != 4:
        print("{} <input filename> <output filename> <depth to search>".format(args[0]))
        exit(1)
    inp, outp, depth = args[1:4]
    with open(inp) as fin:
        start_pos = fin.read()
    return start_pos, outp, depth


def write_output(pos, filename):
    with open(filename, 'w') as fout:
        fout.write(pos)


def check_leaf_node(board, pos, curr_d, max_d, static_func, opening=False):
    if curr_d == max_d or (not opening and (board.num_white(pos) == 2 or board.num_black(pos) == 2)):  # leaf node
        increment_count()
        score = static_func(board, pos)
        #print("{}{}".format("\t"*curr_d, score))
        return score


def maxmin(board, pos, curr_d, max_d, static_func, gen_func, opening):
    #print("{}maxmin {} {} {}".format("\t"*curr_d, pos, curr_d, max_d))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    max_score = -100000
    max_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = minmax(board, child_pos, curr_d+1, max_d, static_func, gen_func, opening)
        if score > max_score:
            max_score = score
            max_pos = child_pos
    #print("{}{} {}".format("\t"*curr_d, max_score, max_pos))
    return max_pos, max_score


def minmax(board, pos, curr_d, max_d, static_func, gen_func, opening):
    #print("{}minmax {} {} {}".format("\t"*curr_d, pos, curr_d, max_d))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    min_score = 100000
    min_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = maxmin(board, child_pos, curr_d+1, max_d, static_func, gen_func, opening)
        if score < min_score:
            min_score = score
            min_pos = child_pos
    #print("{}{} {}".format("\t" * curr_d, min_score, min_pos))
    return min_pos, min_score


def maxmin_ab(board, pos, curr_d, max_d, static_func, gen_func, a, b, opening):
    #print("{}maxmin_ab {} {} {} {} {}".format("\t"*curr_d, pos, curr_d, max_d, a, b))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    max_score = -100000
    max_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = minmax_ab(board, child_pos, curr_d+1, max_d, static_func, gen_func, a, b, opening)
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


def minmax_ab(board, pos, curr_d, max_d, static_func, gen_func, a, b, opening):
    #print("{}minmax_ab {} {} {} {} {}".format("\t" * curr_d, pos, curr_d, max_d, a, b))
    score = check_leaf_node(board, pos, curr_d, max_d, static_func, opening)
    if score is not None:
        return pos, score

    min_score = 100000
    min_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = maxmin_ab(board, child_pos, curr_d+1, max_d, static_func, gen_func, a, b, opening)
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


def improved_mid_black(board, pos):
    return improved_mid_white(board, board.invert_pos(pos))


def improved_mid_white(board, pos):
    howclose = board.mill_status_white(pos)
    hcl = sorted(howclose.items(), key=lambda x: x[1])
    edges = {}
    for t in reversed(hcl):
        if t[1] <= 1:
            break
        for nbr in board.mill_graph.neighbors(t[0]):  # parallel mills
            #print("eval{} {} {}".format(t, nbr, howclose[nbr]))
            mp = mill_potential(board, t, (nbr, howclose[nbr]), pos)
            if mp[0] > 0:
                #print("\t{}".format(mp))
                edges[mp[1]] = mp[0]
    #print(edges)
    return sum(edges.values()) * 100


def edge_potential(board, i, j, pos):
    p0 = pos[board.node_idx(i)]
    p1 = pos[board.node_idx(j)]
    if p0 == 'x' and p1 == 'W':
        return i
    if p1 == 'x' and p0 == 'W':
        return j
    return None


def mill_potential(board, m1, m2, pos):
    if m1[1] == 0 or m2[1] == 0:  # either mill is empty there is no potential move
        return 0, None
    if m1[1] == 1 and m2[1] == 1:  # both mills have just 1 piece, not potential move
        return 0, None

    possibles = []
    for e in board.mill_graph.edges[(m1[0], m2[0])]['nodes']:  # edges that connect the mills
        ep = edge_potential(board, e[0], e[1], pos)
        if ep is not None:
            possibles.append((e,ep))

    for e, ep in possibles:
        if (ep in m1[0] and m1[1] == 2) or \
                (ep in m2[0] and m2[1] == 2):  # a mill would be closed by this move
            return max([m1[1], m2[1]]), e

    return 0, None


def improved_open_white(board, pos):
    howclose = board.mill_status_black(pos)
    hcl = sorted(howclose.items(), key=lambda x: x[1])
    summ = 0
    for t in hcl:
        if t[1] == 2:
            parray = board.parse_mill(t[0])
            for n in parray:
                if pos[board.node_idx(n)] == 'W':
                    #print(t, "blocked by W at ", n)
                    summ += 1
                    break
    return summ


def improved_open_black(board, pos):
    return improved_open_white(board, board.invert_pos(pos))


