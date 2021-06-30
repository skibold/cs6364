from sys import argv

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


def maxmin(board, pos, curr_d, max_d, static_func, gen_func):
    print("{}maxmin {} {} {}".format("\t"*curr_d, pos, curr_d, max_d))
    if curr_d == max_d or board.num_white(pos) == 2 or board.num_black(pos) == 2:  # leaf node
        increment_count()
        score = static_func(board, pos)
        print("{}{}".format("\t"*curr_d, score))
        return pos, score

    max_score = -100000
    max_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = minmax(board, child_pos, curr_d+1, max_d, static_func, gen_func)
        if score > max_score:
            max_score = score
            max_pos = child_pos
    print("{}{} {}".format("\t"*curr_d, max_score, max_pos))
    return max_pos, max_score


def minmax(board, pos, curr_d, max_d, static_func, gen_func):
    print("{}minmax {} {} {}".format("\t"*curr_d, pos, curr_d, max_d))
    if curr_d == max_d or board.num_white(pos) == 2 or board.num_black(pos) == 2:  # leaf node
        increment_count()
        score = static_func(board, pos)
        print("{}{}".format("\t" * curr_d, score))
        return pos, score

    min_score = 100000
    min_pos = ""
    for _, child_pos in gen_func(board, pos, curr_d):
        _, score = maxmin(board, child_pos, curr_d+1, max_d, static_func, gen_func)
        if score < min_score:
            min_score = score
            min_pos = child_pos
    print("{}{} {}".format("\t" * curr_d, min_score, min_pos))
    return min_pos, min_score


def maxmin_ab(board, pos, curr_d, max_d, static_func, gen_func, a, b):
    pass  # todo


def minmax_ab(board, pos, curr_d, max_d, static_func, gen_func, a, b):
    pass  # todo


