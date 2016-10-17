import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import itertools
from transition import Transition
from sets import Set

# Variable ordering [I V H P O]

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

S = prune_states(S)

print S

def create_graph(S):
    # creates a directed graph
    G = nx.DiGraph()
    n_states = len(S)
    T = []
    for orig_ix in range(n_states):
        for dest_ix in range(orig_ix, n_states):
            tr = Transition(S[orig_ix],S[dest_ix])
            if tr.checkValidity():
                T.append(tr)
                G.add_edge(orig_ix,dest_ix)
    return G, T

G, T = create_graph(S)

print ' -----'

s1 = Set([])
s2 = Set([])
s0 = Set([])

for t in T:
    s0.add(str(t.origin))
    s0.add(str(t.destination))

    s1.add(str(t.origin))
    s2.add(str(t.destination))
    print t.prettyprint()

print len(s0)

print len(s1)
print len(s2)

print len(T)

pos = nx.spring_layout(G)

for v in G.nodes():
    G.node[v]['state']=v

nx.draw(G, pos)
node_labels = nx.get_node_attributes(G,'state')
nx.draw_networkx_labels(G, pos, labels = node_labels)
edge_labels = nx.get_edge_attributes(G,'state')
nx.draw_networkx_edge_labels(G, pos, labels = edge_labels)
#plt.savefig('this.png')
plt.show()


