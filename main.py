import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import itertools
from transition import Transition


# 0, plus, max domain for all the variables
var_dom = [0, 1, 2]

# ?, negative, 0, plus for all derivatives
der_dom = [-100,-1,0,1]


# creates full envisionment
st_var = list(itertools.product(var_dom, repeat=5))
st_der = list(itertools.product(der_dom, repeat=5))
states = list(itertools.product(st_var, st_der))


# translates envisionment to np array
S = []
for i in range(len(states)):
    S.append( np.asarray(states[i][0] + states[i][1]))
S = np.asarray(S)

def prune_states(S):
    # number of variables
    nvars = np.shape(S)[1]/2

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
        # checks for equivalent variable
        for i in range(1,nvars):
            for j in range(i+1,nvars):
                if (s[i] != s[j]) or (s[i + nvars] != s[j + nvars]):
                    del_states.append(s_ix)
                    break
    print 'Number of states prunned: ' + str(len(del_states))
    # deletes the invalid states
    S = np.delete(S,del_states, axis=0)
    return S

S = prune_states(S)


def create_graph(S):
    G = nx.DiGraph()
    n_states = len(S)
    for orig_ix in range(n_states):
        for dest_ix in range(orig_ix + 1, n_states):
            tr = Transition(S[orig_ix],S[dest_ix])
            #if valid_transition(S[orig_ix]-S[dest_ix]):
            if tr.checkValidity():
                G.add_edge(orig_ix,dest_ix)
    return G

G = create_graph(S)

pos = nx.spring_layout(G)
nx.draw(G, pos)
plt.show()