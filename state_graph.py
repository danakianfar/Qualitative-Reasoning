import numpy as np
import networkx as nx
from transition import Transition

def prune_states(S):
    # number of variables
    nvars = np.shape(S)[1]/2
    print 'Initial number of states: ' + str(len(S))
    #stores the states to be deleted
    del_states = []
    for s_ix in range(len(S)):
        s = S[s_ix]
        # exogenous variable can not have ambiguous derivative
        if s[nvars] < -1:
            del_states.append(s_ix)
            continue
        for i in range(nvars):
            # if max value then can not have positive derivative
            if s[i] == 2 and s[i+nvars] == 1:
                del_states.append(s_ix)
                break
            #if min value then can not have negative derivative
            if s[i] == 0 and s[i+nvars] == -1:
                del_states.append(s_ix)
                break
        # checks for positive influence
        if not( (s[1+nvars] != 1) or  (s[0] >0)) or ((s[0] == 0) and (s[1+nvars] < -1)):
            del_states.append(s_ix)
            continue
        # checks for equivalent variables V H P O
        for i in range(1,nvars):
            for j in range(i+1,nvars):
                if (s[i] != s[j]) or (s[i + nvars] != s[j + nvars]):
                    del_states.append(s_ix)
                    break

    print 'Number of states prunned: ' + str(len(del_states))
    # deletes the invalid states
    S = np.delete(S,del_states, axis=0)
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
