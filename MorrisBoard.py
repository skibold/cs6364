# Encapsulates the board positions and connectivity
# Valid piece layout
# Valid moves and successor states

import numpy as np
import pandas as pd
import networkx as nx


class Board:
    #static
    pos_lut = ['a0', 'g0', 'b1', 'f1', 'c2', 'e2', 'a3', 'b3', 'c3', 'e3', 'f3', 'g3', 'c4', 'd4', 'e4', 'b5', 'd5', 'f5', 'a6', 'd6', 'g6']
    src =  ['a0', 'a0', 'a0', 'g0', 'b1', 'b1', 'b1', 'f1', 'c2', 'c2', 'e2', 'a3', 'a3', 'b3', 'b3', 'c3', 'e3', 'e3', 'f3', 'f3', 'g3', 'd4', 'd4', 'd4', 'b5', 'd5', 'd5', 'a6', 'd6']
    dest = ['a3', 'g0', 'b1', 'g3', 'b3', 'f1', 'c2', 'f3', 'c3', 'e2', 'e3', 'a6', 'b3', 'b5', 'c3', 'c4', 'e4', 'f3', 'f5', 'g3', 'g6', 'e4', 'c4', 'd5', 'd5', 'd6', 'f5', 'd6', 'g6']
    mills = [['a0', 'a3', 'a6'], ['b1', 'b3', 'b5'], ['c2', 'c3', 'c4'], ['d4', 'd5', 'd6'], ['e2', 'e3', 'e4'], ['f1', 'f3', 'f5'], ['g0', 'g3', 'g6'],
             ['a3', 'b3', 'c3'], ['e3', 'f3', 'g3'], ['c4', 'd4', 'e4'], ['b5', 'd5', 'f5'], ['a6', 'd6', 'g6'], ['a0', 'b1', 'c2']]

    def __init__(self):
        self.df = pd.DataFrame({"src": self.src, "dest": self.dest})
        self.mill_mat = np.zeros([len(self.mills), len(self.pos_lut)])
        for i, mill in enumerate(self.mills):
            n = [self.pos_lut.index(m) for m in mill]
            self.mill_mat[i][n] = 1

        self.mill_dict = {}
        for n in self.pos_lut:
            self.mill_dict[n] = []
            for i, m in enumerate(self.mills):
                if n in m:
                    self.mill_dict[n].append(i)

        self.mill_graph = self.mk_mill_graph()

    def mk_mill_graph(self):
        edges = {}
        for m in self.mills:
            for mi in m:
                for n in self.neighbors(mi):
                    for mj in self.mill_dict[n]:
                        src = ''.join(m)
                        dest = ''.join(self.mills[mj])
                        if src != dest and len(set(m).intersection(self.mills[mj])) == 0:
                            e1 = (''.join(m), ''.join(self.mills[mj]))
                            e2 = (''.join(self.mills[mj]), ''.join(m))
                            if e1 in edges:  # and (mi, n) not in edges[e1]['nodes']:
                                if not ((mi, n) in edges[e1]['nodes'] or (n, mi) in edges[e1]['nodes']):
                                    edges[e1]['weight'] += 1
                                    edges[e1]['nodes'].append((mi, n))
                            elif e2 in edges:  # and (n, mi) not in edges[e2]['nodes']:
                                if not ((mi, n) in edges[e2]['nodes'] or (n, mi) in edges[e2]['nodes']):
                                    edges[e2]['weight'] += 1
                                    edges[e2]['nodes'].append((n, mi))
                            else:
                                edges[(''.join(m), ''.join(self.mills[mj]))] = {'weight': 1, 'nodes': [(mi, n)]}
        dod = {}
        for k, v in edges.items():
            if k[0] not in dod:
                dod[k[0]] = {}
            dod[k[0]][k[1]] = v
        return nx.from_dict_of_dicts(dod)

    def node_at(self, i:int):
        assert i<len(self.pos_lut), "Only {} positions; {} is out of range.".format(len(self.pos_lut), i)
        return self.pos_lut[i]

    def node_idx(self, s:str):
        assert s in self.pos_lut, "Position {} not valid.".format(s)
        return self.pos_lut.index(s)

    def validate_pos(self, pos):
        assert len(pos) == 21, "Position {} must be 21 chars.".format(pos)

    def get_labeled_pos(self, pos):
        return list(zip(self.pos_lut, list(pos)))

    @staticmethod
    def invert_pos(pos:str):
        pos = pos.replace('B', 'w')
        pos = pos.replace('W', 'B')
        return pos.replace('w', 'W')

    def neighbors(self, v):
        if type(v) is int:
            v = self.node_at(v)
        assert type(v) is str, "Unrecognized node {}".format(v)
        e = list(self.df[self.df.src==v]['dest'])  # out edges
        e.extend(list(self.df[self.df.dest==v]['src']))  # in edges
        return set(e)

    def piece_at(self, v, pos):
        if type(v) is str:
            v = self.node_idx(v)
        assert type(v) is int, "Unrecognized node {}".format(v)
        return pos[v]

    def gen_add_4_white(self, pos):
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

    def gen_add_4_black(self, pos):
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

    def gen_move_4_white(self, pos):
        for i, p in enumerate(pos):
            if p == 'W':
                #print("neighbors of ", self.node_at(i))
                for n in self.neighbors(i):
                    #print("\t{} {}".format(n, self.piece_at(n)))
                    if self.piece_at(n, pos) == 'x':
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

    def gen_move_4_black(self, pos):
        for j, p in self.gen_move_4_white(self.invert_pos(pos)):
            yield j, self.invert_pos(p)

    def gen_hop_4_white(self, pos):
        for i, p in enumerate(pos):  # todo this could be done faster
            if p == 'W':
                for j, q in enumerate(pos):  # todo this could be done faster
                    if i == j:
                        continue
                    if q == 'x':
                        rv = list(pos)
                        rv[i] = 'x'
                        rv[j] = 'W'
                        #print("hop {} -> {}".format(self.node_at(i), self.node_at(j)))
                        newp = ''.join(rv)
                        if self.close_mill(j, newp):
                            for newnewp in self.remove_piece(j, newp):
                                yield j, newnewp
                        else:
                            yield j, newp

    def gen_hop_4_black(self, pos):
        for j, p in self.gen_hop_4_white(self.invert_pos(pos)):
            yield j, self.invert_pos(p)

    def close_mill(self, i, pos):
        if pos[i] == 'x':
            return False
        val = pos[i]
        ipos = np.array([1 if j == val else 0 for j in pos])
        loc = np.where(self.mill_mat[:, i] == 1)[0]
        return np.any(np.matmul(self.mill_mat[loc], ipos) == 3)

    def close_mill(self, i, pos):
        if pos[i] == 'x':
            return False
        n = self.node_at(i)
        val = pos[i]
        for mill in self.mills:
            if n in mill and\
               sum([1 if pos[self.node_idx(m)] == val else 0 for m in mill]) == 3:
                #print(mill)
                return True
        return False

    def remove_piece(self, i, pos):
        val = pos[i]
        #print("{} at pos {} closed a mill, pos would've been {}, but now we get to remove pieces".format(val, self.node_at(i), pos))
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
            #print("all opponents' pieces are in mills, yield the original position")
            yield pos

    @staticmethod
    def num_white(pos):
        return pos.count('W')

    @staticmethod
    def num_black(pos):
        return pos.count('B')

    def num_white_moves(self, pos):
        nw = self.num_white(pos)
        if nw <= 2:
            return 0
        if nw == 3:
            return len(list(self.gen_hop_4_white(pos)))
        return len(list(self.gen_move_4_white(pos)))

    def num_black_moves(self, pos):
        nb = self.num_black(pos)
        if nb <= 2:
            return 0
        if nb == 3:
            return len(list(self.gen_hop_4_black(pos)))
        return len(list(self.gen_move_4_black(pos)))

    def open_estimate_white(self, pos):
        return self.num_white(pos) - self.num_black(pos)

    def mid_end_estimate_white(self, pos):
        if self.num_black(pos) <= 2:
            return 10000  # inf, win
        if self.num_white(pos) <= 2:
            return -10000  # -inf, loss
        if self.num_black_moves(pos) == 0:
            return 10000  # inf, win
        return 1000 * (self.num_white(pos) - self.num_black(pos)) - self.num_black_moves(pos)

    def open_estimate_black(self, pos):
        return self.open_estimate_white(self.invert_pos(pos))

    def mid_end_estimate_black(self, pos):
        return self.mid_end_estimate_white(self.invert_pos(pos))

    def mill_status_white(self, pos):
        int_pos = [1 if j == 'W' else 0 for j in pos]
        mill_count = np.matmul(self.mill_mat, int_pos)
        return dict(zip([''.join(m) for m in self.mills], mill_count))

    def mill_status_black(self, pos):
        return self.mill_status_white(self.invert_pos(pos))

    @staticmethod
    def parse_mill(mill):
        return [mill[:2], mill[2:4], mill[4:]]

    @staticmethod
    def join_mill(mill):
        return ''.join(mill)
