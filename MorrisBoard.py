import numpy as np
import networkx as nx
import pandas as pd
from copy import deepcopy

class Board:
    #static
    pos_lut = ['a0', 'g0', 'b1', 'f1', 'c2', 'e2', 'a3', 'b3', 'c3', 'e3', 'f3', 'g3', 'c4', 'd4', 'e4', 'b5', 'd5', 'f5', 'a6', 'd6', 'g6']
    src =  ['a0', 'a0', 'a0', 'g0', 'b1', 'b1', 'b1', 'f1', 'c2', 'c2', 'e2', 'a3', 'a3', 'b3', 'b3', 'c3', 'e3', 'e3', 'f3', 'f3', 'g3', 'd4', 'd4', 'd4', 'b5', 'd5', 'd5', 'a6', 'd6']
    dest = ['a3', 'g0', 'b1', 'g3', 'b3', 'f1', 'c2', 'f3', 'c3', 'e2', 'e3', 'a6', 'b3', 'b5', 'c3', 'c4', 'e4', 'f3', 'f5', 'g3', 'g6', 'e4', 'c4', 'd5', 'd5', 'd6', 'f5', 'd6', 'g6']
    mills = [['a0', 'a3', 'a6'], ['b1', 'b3', 'b5'], ['c2', 'c3', 'c4'], ['d4', 'd5', 'd6'], ['e2', 'e3', 'e4'], ['f1', 'f3', 'f5'], ['g0', 'g3', 'g6'],
             ['a3', 'b3', 'c3'], ['e3', 'f3', 'g3'], ['c4', 'd4', 'e4'], ['b5', 'd5', 'f5'], ['a6', 'd6', 'g6'], ['a0', 'b1', 'c2']]

    def __init__(self, initial_pos:str=None):
        #self.g = nx.from_pandas_edgelist(pd.DataFrame({"src": self.src, "dest": self.dest}), 'src', 'dest')
        self.df = pd.DataFrame({"src": self.src, "dest": self.dest})
        if initial_pos is not None and len(initial_pos) == 21:
            #self.set_pos(initial_pos)
            self.curr_pos = initial_pos
        else:
            #self.set_pos(''.join(['x']*21))
            self.curr_pos = ''.join(['x']*21)

    def node_at(self, i:int):
        assert i<len(self.pos_lut), "Only {} positions; {} is out of range.".format(len(self.pos_lut), i)
        return self.pos_lut[i]

    def node_idx(self, s:str):
        assert s in self.pos_lut, "Position {} not valid.".format(s)
        return self.pos_lut.index(s)

    def set_pos(self, pos:str):
        assert len(pos) == 21, "Position {} must be 21 chars.".format(pos)
        self.curr_pos = pos
        #for p in range(21):
        #    self.g.nodes[self.pos_lut[p]]['piece'] = pos[p]

    def get_pos(self):
        return self.curr_pos
        #return ''.join([self.g.nodes[p]['piece'] for p in self.pos_lut])

    def invert_pos(self, pos:str):
        pos = pos.replace('B', 'w')
        pos = pos.replace('W', 'B')
        return pos.replace('w', 'W')

    def invert_board(self):
        self.set_pos(self.invert_pos(self.get_pos()))

    def neighbors(self, v):
        if type(v) is int:
            v = self.node_at(v)
        assert type(v) is str, "Unrecognized node {}".format(v)
        e = self.df[self.df.src==v]['dest'].to_list()  # out edges
        e.extend(self.df[self.df.dest==v]['src'].to_list())  # in edges
        return set(e)

    def piece_at(self, v):
        if type(v) is str:
            v = self.node_idx(v)
        assert type(v) is int, "Unrecognized node {}".format(v)
        return self.curr_pos[v]

    def gen_add_4_white(self):
        pos = self.get_pos()
        for i, p in enumerate(pos):
            if p == 'x':
                rv = list(pos)
                rv[i] = 'W'
                newp = ''.join(rv)
                if self.close_mill(i, newp):
                    for newnewp in self.remove_piece(i, newp):
                        yield i, newnewp
                else:
                    yield i, newp

    def gen_add_4_black(self):
        pos = self.get_pos()
        for i, p in enumerate(pos):
            if p == 'x':
                rv = list(pos)
                rv[i] = 'B'
                newp = ''.join(rv)
                if self.close_mill(i, newp):
                    for newnewp in self.remove_piece(i, newp):
                        yield i, newnewp
                else:
                    yield i, newp

    def gen_move_4_white(self):
        pos = self.get_pos()
        for i, p in enumerate(pos):
            if p == 'W':
                #print("neighbors of ", self.node_at(i))
                for n in self.neighbors(i):
                    #print("\t{} {}".format(n, self.piece_at(n)))
                    if self.piece_at(n) == 'x':
                        j = self.node_idx(n)
                        rv = list(pos)
                        rv[i] = 'x'
                        rv[j] = 'W'
                        newp = ''.join(rv)
                        if self.close_mill(j, newp):
                            for newnewp in self.remove_piece(j, newp):
                                yield j, newnewp
                        else:
                            yield j, newp

    def gen_move_4_black(self):
        self.invert_board()
        for j, p in self.gen_move_4_white():
            yield j, self.invert_pos(p)
        self.invert_board()

    def gen_hop_4_white(self):
        pos = self.get_pos()
        for i, p in enumerate(pos):
            if p == 'W':
                for j, q in enumerate(pos):
                    if i == j:
                        continue
                    if q == 'x':
                        rv = list(pos)
                        rv[i] = 'x'
                        rv[j] = 'W'
                        newp = ''.join(rv)
                        if self.close_mill(j, newp):
                            for newnewp in self.remove_piece(j, newp):
                                yield j, newnewp
                        else:
                            yield j, newp

    def gen_hop_4_black(self):
        self.invert_board()
        for j, p in self.gen_hop_4_white():
            yield j, self.invert_pos(p)
        self.invert_board()

    def close_mill(self, i, pos):
        n = self.node_at(i)
        val = pos[i]
        for mill in self.mills:
            if n in mill and\
               sum([1 if pos[self.node_idx(m)] == val else 0 for m in mill]) == 3:
                print(mill)
                return True
        return False

    def remove_piece(self, i, pos):
        val = pos[i]
        print("{} at pos {} closed a mill, pos would've been {}, but now we get to remove pieces".format(val, self.node_at(i), pos))
        c = 0
        for j in range(21):
            if i == j:
                continue
            if pos[j] not in [val, 'x'] and not self.close_mill(j, pos):
                c += 1
                rv = list(pos)
                rv[j] = 'x'
                yield ''.join(rv)
        if c == 0:
            print("all opponents' pieces are in mills, yield the original position")
            yield pos

    def num_white(self, pos=None):
        if pos is not None:
            return pos.count('W')
        return self.get_pos().count('W')

    def num_black(self, pos=None):
        if pos is not None:
            return pos.count('B')
        return self.get_pos().count('B')

    def num_black_moves(self, pos=None):
        bak = None
        if pos is not None:
            bak = self.get_pos()
            self.set_pos(pos)
        est = len(list(self.gen_move_4_black()))
        if bak is not None:
            self.set_pos(bak)
        return est

    def open_estimate_white(self, pos=None):
        return self.num_white(pos) - self.num_black(pos)

    def mid_end_estimate_white(self, pos=None):
        if self.num_black(pos) <= 2:
            return 10000  # inf, win
        if self.num_white(pos) <= 2:
            return -10000  # -inf, loss
        if self.num_black_moves(pos) == 0:
            return 10000  # inf, win
        return 1000 * (self.num_white(pos) - self.num_black(pos)) - self.num_black_moves(pos)

    def open_estimate_black(self, pos=None):
        if pos is not None:
            pos = self.invert_pos(pos)
        self.invert_board()
        est = self.open_estimate_white(pos)
        self.invert_board()
        if pos is not None:
            pos = self.invert_pos(pos)
        return est

    def mid_end_estimate_black(self, pos=None):
        if pos is not None:
            pos = self.invert_pos(pos)
        self.invert_board()
        est = self.mid_end_estimate_white(pos)
        self.invert_board()
        if pos is not None:
            pos = self.invert_pos(pos)
        return est
