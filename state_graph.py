import numpy as np
import networkx as nx
import pygraphviz as pgv
from itertools import chain, combinations

val_idx = range(5)
delta_idx = range(5, 10)
numVars = len(val_idx)
i = 0
v = 1
h = 2
p = 3
o = 4
di = 5
dv = 6
dh = 7
dp = 8
do = 9

# Encoding
def_max = 2
def_zero = 0
def_plus = 1
def_neg = -1
def_amb = -9


def compactRepresentation(vector):
    return [vector[z] for z in [i, v, di, dv]]


def compactTransition(transition):
    return str(compactRepresentation(transition.origin)) + '   -->    ' + str(
        compactRepresentation(transition.transition)) + '   -->    ' + str(
        compactRepresentation(transition.destination))


def d(x):
    if x == 0:
        return '0'
    elif x == 1:
        return '+'
    elif x == 2:
        return 'm'
    elif x == -1:
        return '-'
    elif x < -5 or x > 5:
        return '?'
    else:
        print 'what? ' + str(x)


class Transition():
    def __init__(self, origin, destination):
        self.transition = destination - origin
        self.origin = origin
        self.destination = destination
        self.numVars = self.transition.shape[0] / 2

    def prettyprint(self):
        res = '------\n'
        for j in range(len(val_idx)):
            res += d(self.origin[j]) + d(self.origin[j + numVars]) + '\t' + d(self.transition[j]) + d(
                self.transition[j + numVars]) + '\t' + d(self.destination[j]) + d(self.destination[j + numVars]) + '\n'
        res += '------'
        return res


def prop_der(transition):
    copy = np.array(transition.origin.copy(), 'float64')

    # split on interval->point, point->interval
    intervals = copy[val_idx] % 2
    points = 1 - intervals

    # split intervals to basis vectors
    eye = np.eye(transition.numVars)
    bases = eye[np.where(intervals > 0)]
    possible_updates = []

    for combo in chain.from_iterable(combinations(bases, r) for r in range(len(bases) + 1)):
        update = np.array(points, 'float64')
        for x in list(combo):
            update += x
        possible_updates.append(update)

    possible_new_states = []
    for x in possible_updates:
        temp_state = copy.copy()
        temp_state[val_idx] += x * copy[delta_idx]

        # not increase at max
        max_idx = np.where(temp_state[val_idx] == 2)[0]
        for idx in max_idx:
            if temp_state[idx + transition.numVars] == 1:
                temp_state[idx + transition.numVars] = 0

        # not decrease at min
        min_idx = np.where(temp_state[val_idx] == 0)[0]
        for idx in min_idx:
            if temp_state[idx + transition.numVars] == -1:
                temp_state[idx + transition.numVars] = 0

        possible_new_states.append(temp_state.tolist())

    possible_new_states = [list(x) for x in set(tuple(x) for x in possible_new_states)]

    return np.array(possible_new_states, 'float64')


def prop_inf(transition, state, I, dom_der):
    st_list = []

    for i in range(transition.numVars):
        if sum(abs(I[:, i])) > 0:
            for j in dom_der[i]:
                copy = list(state)
                copy[i + transition.numVars] = j
                st_list.append(copy)

    return st_list


def prop_prop(transition, state, P):
    st_list = []
    state = np.array(state)

    for i in range(transition.numVars):
        for j in range(transition.numVars):
            if P[i, j] != 0:
                state[j + transition.numVars] = P[i, j] * state[i + transition.numVars]
                if abs(state[j + transition.numVars]) > 5:
                    state[j + transition.numVars] = -9
                st_list.append(state.tolist())

    return st_list


def exogenous_change(S, transition, dom_der):
    S_exog = []

    for state in S:
        for der in dom_der[0]:
            copy = state.copy()
            if copy[transition.numVars] != der:
                copy[transition.numVars] = der
                S_exog.append(copy.tolist())
    return S_exog


def checkTransitionValidity(transition, I, P, dom_der, orig_ix, dest_ix):

    if 2 in abs(transition.transition):
        print 'Result of epsilon continuity: %s %d ---> %d' % (False, orig_ix, dest_ix)
        return False

    s1 = prop_der(transition)

    s1 = partial_pruning(s1, I).tolist()

    if transition.destination.tolist() in s1:
        # delta prop necessary and destination is a forced move
        print 'Result of derivative propagation: %s %d ---> %d' % (True, orig_ix, dest_ix)
        return True

    s2 = []
    for s in s1:
        s2 += prop_inf(transition, s, I, dom_der)

    S_prime = np.asarray(s2)
    s2 = partial_pruning2(S_prime, I).tolist()

    s3 = []
    for s in s2:
        s3 += prop_prop(transition, s, P)
    s3 = [list(x) for x in set(tuple(x) for x in s3)]

    S_prime = np.asarray(s3)
    S_pruned = prune_states(S_prime, I)

    if transition.destination.tolist() in S_pruned.tolist():
        print 'Result of I and P propagation: %s %d ---> %d' % (True, orig_ix, dest_ix)
        return True
    else:
        result = is_exogenous(transition)
        if result:
            print 'Result of exogenous influence: %s %d ---> %d' % (str(result), orig_ix, dest_ix)
        else:
            print 'Invalid transition: %s %d ---> %d' % (str(result), orig_ix, dest_ix)
        return result


def is_exogenous(transition):

    if sum(abs(transition.transition[val_idx])) != 0 or sum(abs(transition.transition[numVars+1:-1])) != 0 or transition.transition[numVars] == 0:
        return False

    if (transition.destination[v] == 2 and transition.destination[dv] == -1) or (transition.destination[v] == 0 and transition.destination[dv] == 1):
       return False

    return True

def partial_pruning(S, I):
    # number of variables
    nvars = np.shape(S)[1] / 2
    init_states = len(S)

    # stores the states to be deleted
    del_states = set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i + nvars] == 1:
                del_states.add(s_ix)
                break
            # if min value then can not have negative derivative
            if s[i] == 0 and s[i + nvars] == -1:
                del_states.add(s_ix)
                break

        # checks for value correspondence in variables V H P O
        for i in range(1, nvars):
            for j in range(1, nvars):
                if (s[i] != s[j]):
                    del_states.add(s_ix)
                    break

    S = np.delete(S, list(del_states), axis=0)

    return S


def partial_pruning2(S, I):
    # number of variables
    nvars = np.shape(S)[1] / 2
    init_states = len(S)

    # stores the states to be deleted
    del_states = set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i + nvars] == 1:
                del_states.add(s_ix)
                break
            # if min value then can not have negative derivative
            if s[i] == 0 and s[i + nvars] == -1:
                del_states.add(s_ix)
                break

        # checks for value correspondence in variables V H P O
        for i in range(1, nvars):
            for j in range(1, nvars):
                if (s[i] != s[j]):
                    del_states.add(s_ix)
                    break

    S = np.delete(S, list(del_states), axis=0)

    del_states1 = set([])
    del_states2 = set([])

    for s_ix in range(len(S)):
        s = S[s_ix]

        # checks for influence relationships
        for j in range(nvars):

            # if nothing influences the variable, it can change freely
            if sum(abs(I[:, j])) == 0:
                continue

            influences = set([])

            for i in range(nvars):
                # checks it there is an influence and the variable has value diff to zero
                if I[i][j] != 0 and s[i] != 0:
                    influences.add(I[i][j])

            # if no influences on the variable and no variables have values, derivative has to be zero
            if len(influences) == 0 and sum(abs(s[0:nvars])) == 0 and s[j + nvars] != 0:
                del_states1.add(s_ix)
                continue

            # all influences have same sign, derivative has to be in that direction
            if len(influences) == 1 and influences.pop() != s[j + nvars]:
                del_states2.add(s_ix)
                continue

    del_states = del_states1 | del_states2

    # deletes the invalid states
    S = np.delete(S, list(del_states), axis=0)

    return S


def prune_states(S, I):
    # number of variables
    nvars = np.shape(S)[1] / 2
    init_states = len(S)

    # stores the states to be deleted
    del_states = set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i + nvars] == 1:
                del_states.add(s_ix)
                break
            # if min value then can not have negative derivative
            if s[i] == 0 and s[i + nvars] == -1:
                del_states.add(s_ix)
                break

        # checks for equivalent variables V H P O
        for i in range(1, nvars):
            for j in range(1, nvars):
                if (s[i] != s[j]) or (s[i + nvars] != s[j + nvars]):
                    del_states.add(s_ix)
                    break

    S = np.delete(S, list(del_states), axis=0)

    del_states1 = set([])
    del_states2 = set([])

    for s_ix in range(len(S)):
        s = S[s_ix]

        # checks for influence relationships
        for j in range(nvars):

            # if nothing influences the variable, it can change freely
            if sum(abs(I[:, j])) == 0:
                continue

            influences = set([])

            for i in range(nvars):
                # checks it there is an influence and the variable has value diff to zero
                if I[i][j] != 0 and s[i] != 0:
                    influences.add(I[i][j])

            # if no influences on the variable and no variables have values, derivative has to be zero
            if len(influences) == 0 and s[j + nvars] != 0:
                del_states1.add(s_ix)
                break

            # all influences have same sign, derivative has to be in that direction
            if len(influences) == 1 and influences.pop() != s[j + nvars]:
                del_states2.add(s_ix)
                break

    del_states = del_states1 | del_states2

    # deletes the invalid states
    S = np.delete(S, list(del_states), axis=0)

    return S


def create_graph(S, I, P, dom_der):
    # creates a directed graph

    print '++ Transition Validity Log Start ++\n'
    G2 = pgv.AGraph(directed=True, overlap=False, splines=True, sep=+1.2, normalize=True, smoothing='avg_dist')

    G = nx.MultiDiGraph()
    n_states = len(S)
    T = []

    edgelist = []
    for orig_ix in range(n_states):
        for dest_ix in range(n_states):
            # creates transition from orig to dest
            tr = Transition(S[orig_ix], S[dest_ix])

            # if transition is valid, then add it to the graph
            if checkTransitionValidity(tr, I, P, dom_der, orig_ix, dest_ix):
                T.append(tr)
                # print len(T)
                G.add_edge(orig_ix, dest_ix)
                edgelist.append([orig_ix, dest_ix])

    G2.add_edges_from(edgelist)

    for pair in edgelist:
        col = 'forestgreen'
        if pair[0] % 3 == 1:
            col = 'dodgerblue3'
        if pair[0] % 3 == 2:
            col = 'black'
        G2.get_edge(pair[0], pair[-1]).attr['color'] = col
        G2.get_edge(pair[0], pair[-1]).attr['constraint'] = False

    pos1 = nx.spring_layout(G)

    for k, v in pos1.iteritems():
        G2.get_node(k).attr['fontsize'] = 25
        G2.get_node(k).attr['width'] = 0.5
        G2.get_node(k).attr['shape'] = 'circle'
        G2.get_node(k).attr['color'] = 'red'


    G2.layout(prog='neato')
    fname = 'state_graph.png'
    G2.draw(fname)

    print '\n++ Transition Validity Log End ++'

    print '\n*** State graph stored in file: ' + fname +' ***\n'

    return G, T, G2
