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

    for ix in range(len(S)):
        print str(ix) + ' -- ' + str(S[ix,[0,1,5,6]])

    del_states1 = Set([])
    del_states2 = Set([])
    del_states3 = Set([])

    for s_ix in range(len(S)):
        s = S[s_ix]
        # checks for influence relationships
        for j in range(nvars):
            influences = Set([])

            for i in range(nvars):
                if I[i][j] != 0 and s[i] != 0:
                    influences.add(I[i][j])

            #if len(influences) == 0 and s[j+nvars] != 0:
            #    del_states1.add(s_ix)
            #    continue

            #mixed signs
            if len(influences) == 2 and not(s[j+nvars] < -1):
                del_states2.add(s_ix)
                continue

            #same sign
            if len(influences) == 1 and influences.pop() != s[j + nvars]:
                del_states3.add(s_ix)
                continue

    print '***********'

    print list(del_states1)
    print list(del_states2)
    print list(del_states3)
    print '+++++++++++'

    del_states = del_states1 | del_states2 | del_states3
    print S[list(del_states)]
    print '***********'

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
            tr = Transition(S[orig_ix],S[dest_ix])
            if tr.checkValidity():
                T.append(tr)
                G.add_edge(orig_ix,dest_ix)
    return G, T
