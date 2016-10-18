import numpy as np
import networkx as nx
from transition import Transition
from sets import Set

def prune_states(S,I):
    # number of variables
    nvars = np.shape(S)[1]/2
    init_states = len(S)

    print 'Initial number of states: ' + str(len(S))

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
    print 'Number of states prunned: ' + str(init_states-len(S))
    print 'Final number of states: ' + str(len(S))

    return S


def create_graph(S):
    # creates a directed graph
    G = nx.MultiDiGraph()
    n_states = len(S)
    T = []
    for orig_ix in range(n_states):
        for dest_ix in range(n_states):
            # creates transition from orig to dest
            tr = Transition(S[orig_ix],S[dest_ix])

            #if transition is valid, then add it to the graph
            if tr.checkValidity():
                T.append(tr)
                G.add_edge(orig_ix,dest_ix)
    return G, T
