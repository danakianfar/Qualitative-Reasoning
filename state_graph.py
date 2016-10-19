import numpy as np
import networkx as nx
from sets import Set
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
        print 'what? '+str(x)

class Transition():

    def __init__(self, origin, destination):
        self.transition = destination - origin
        self.origin = origin
        self.destination = destination
        self.numVars = self.transition.shape[0] / 2


    def prettyprint(self):
        res = '------\n'
        for j in range(len(val_idx)):
            res += d(self.origin[j])+d(self.origin[j+numVars])+'\t'+d(self.transition[j])+d(self.transition[j+numVars])+'\t'+d(self.destination[j])+d(self.destination[j+numVars])+'\n'
        res += '------'
        return res

def prop_der(transition):
    copy = np.array(transition.origin.copy(),'float64')
    #
    # copy[np.where(copy < -5)] = 0

    # split on interval->point, point->interval
    intervals = copy[val_idx] % 2
    points = 1 - intervals


    # split intervals to basis vectors
    eye = np.eye(transition.numVars)
    bases = eye[np.where(intervals>0)]
    possible_updates = []

    for combo in chain.from_iterable(combinations(bases, r) for r in range(len(bases) + 1)):
        update = np.array(points,'float64')
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

    return possible_new_states


def prop_inf(transition, state, I, dom_der):

    st_list = []

    for i in range(transition.numVars):
        if sum(abs(I[:,i])) > 0:
            for j in dom_der[i]:
                copy = list(state)
                copy[i+transition.numVars] = j
                st_list.append(copy)

    return st_list


def prop_prop(transition, state, P):

    st_list = []
    state = np.array(state)

    for i in range(transition.numVars):
        for j in range(transition.numVars):
            if P[i,j] != 0:
                state[j + transition.numVars] = P[i,j] * state[i + transition.numVars]
                if abs(state[j + transition.numVars]) > 5:
                    state[j + transition.numVars] = -9
                st_list.append(state.tolist())

    return st_list


def checkTransitionValidity(transition, I, P, dom_der):


    s1 = prop_der(transition)


    s2 = []

    for s in s1:
        s2 += prop_inf(transition, s,I,dom_der)


    S_prime = np.asarray(s2)
    s2 = partial_pruning(S_prime, I).tolist()


    s3 = []

    for s in s2:
        s3 += prop_prop(transition, s, P)


    S_prime = np.asarray(s3)

    S_pruned = prune_states(S_prime, I).tolist()


    if transition.destination.tolist() in S_pruned: # or transition.origin.tolist() in S_pruned:
        return True, 0

    if not transition.destination.tolist() in S_pruned and not transition.origin.tolist() in S_pruned:
        print '!!! Invalid by epsilon rule: forced to apply derivative on point->interval: \n O: %s \n T: %s \n D: %s \n -----' % (transition.origin, transition.transition, transition.destination)
        return False, 5

    return False, 1

def partial_pruning(S,I):
    # number of variables
    nvars = np.shape(S)[1]/2
    init_states = len(S)

    #stores the states to be deleted
    del_states = Set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i+nvars] == 1:
                del_states.add(s_ix)
                break
            #if min value then can not have negative derivative
            if s[i] == 0 and s[i+nvars] == -1:
                del_states.add(s_ix)
                break

    S = np.delete(S, list(del_states), axis=0)

    del_states1 = Set([])
    del_states2 = Set([])

    for s_ix in range(len(S)):
        s = S[s_ix]

        # checks for influence relationships
        for j in range(nvars):

            # if nothing influences the variable, it can change freely
            if sum(abs(I[:, j])) == 0:
                continue

            influences = Set([])

            for i in range(nvars):
                # checks it there is an influence and the variable has value diff to zero
                if I[i][j] != 0 and s[i] != 0:
                    influences.add(I[i][j])

            # if no influences on the variable and no variables have values, derivative has to be zero
            if len(influences) == 0 and sum(abs(s[0:nvars])) == 0 and s[j+nvars] != 0 :
                del_states1.add(s_ix)
                continue

            # all influences have same sign, derivative has to be in that direction
            if len(influences) == 1 and influences.pop() != s[j + nvars]:
                del_states2.add(s_ix)
                continue

    del_states = del_states1 | del_states2

    # deletes the invalid states
    S = np.delete(S,list(del_states), axis=0)

    return S


def prune_states(S,I):
    # number of variables
    nvars = np.shape(S)[1]/2
    init_states = len(S)

    # print 'Initial number of states: ' + str(len(S))

    #stores the states to be deleted
    del_states = Set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i+nvars] == 1:
                del_states.add(s_ix)
                break
            #if min value then can not have negative derivative
            if s[i] == 0 and s[i+nvars] == -1:
                del_states.add(s_ix)
                break

        # checks for equivalent variables V H P O
        for i in range(1, nvars):
            for j in range(1, nvars):
                if (s[i] != s[j]) or (s[i + nvars] != s[j + nvars]):
                    del_states.add(s_ix)
                    break

    S = np.delete(S, list(del_states), axis=0)

    del_states1 = Set([])
    del_states2 = Set([])

    for s_ix in range(len(S)):
        s = S[s_ix]

        # checks for influence relationships
        for j in range(nvars):

            # if nothing influences the variable, it can change freely
            if sum(abs(I[:, j])) == 0:
                continue

            influences = Set([])

            for i in range(nvars):
                # checks it there is an influence and the variable has value diff to zero
                if I[i][j] != 0 and s[i] != 0:
                    influences.add(I[i][j])

            # if no influences on the variable and no variables have values, derivative has to be zero
            if len(influences) == 0 and sum(abs(s[0:nvars])) == 0 and s[j+nvars] != 0 :
                del_states1.add(s_ix)
                continue

            # all influences have same sign, derivative has to be in that direction
            if len(influences) == 1 and influences.pop() != s[j + nvars]:
                del_states2.add(s_ix)
                continue

    del_states = del_states1 | del_states2

    # deletes the invalid states
    S = np.delete(S,list(del_states), axis=0)
    # print 'Number of states prunned: ' + str(init_states-len(S))
    # print 'Final number of states: ' + str(len(S))

    return S


def create_graph(S, I, P, dom_der):
    # creates a directed graph
    G = nx.MultiDiGraph()
    n_states = len(S)
    T = []

    epsilon = set([])
    epsilonFake = set([])
    delta= set([])
    ipos = set([])
    ineg = set([])

    for orig_ix in range(n_states):
        for dest_ix in range(n_states):
            # creates transition from orig to dest
            tr = Transition(S[orig_ix],S[dest_ix])

            #if transition is valid, then add it to the graph
            validity, num = checkTransitionValidity(tr ,I, P, dom_der)
            if validity:
                T.append(tr)
                # print len(T)
                G.add_edge(orig_ix,dest_ix)
            else:
                if num == 1:
                    epsilonFake.add(tr)
                elif num == 2:
                    delta.add(tr)
                elif num == 3:
                    ipos.add(tr)
                elif num == 4:
                    ineg.add(tr)
                elif num == 5:
                    epsilon.add(tr)

    return G, T, (epsilonFake,delta, ipos, ineg, epsilon)
