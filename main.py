import numpy as np
import matplotlib.pyplot as plt
import itertools
from state_graph import *
from sets import Set

# Variable ordering [I V H P O]

# 0, plus, max domain for all the variables
var_dom = [0.0, 1.0, 2.0]

# ?, negative, 0, plus for all derivatives
der_dom = [-9.0,-1.0,0.0,1.0]

# creates full envisionment
st_var = list(itertools.product(var_dom, repeat=5))
st_der = list(itertools.product([-1,0,1], [-9,-1,0,1], [-9,-1,0,1], [-9,-1,0,1], [-9,-1,0,1]))
states = list(itertools.product(st_var, st_der))

# translates envisionment to np array
S = []
for i in range(len(states)):
    S.append( np.asarray(states[i][0] + states[i][1]))
S = np.asarray(S)

# Matrix of influence dependencies (row influences column): +1 I+, -1 I-, 0 no relation
I = np.array([[0, 1, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, -1, 0, 0, 0]])

# Matrix of proportionality dependencies (row influences column): +1 I+, -1 I-, 0 no relation
P = np.array([[0, 0, 0, 0, 0],
              [0, 0, 1, 0, 0],
              [0, 0, 0, 1, 0],
              [0, 0, 0, 0, 1],
              [0, 0, 0, 0, 0]])

S = prune_states(S,I)

print S

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
    #print t.prettyprint()

print 'Total: ' + str(len(s0))
print 'Origin: ' + str(len(s1))
print 'Destinations: ' + str(len(s2))
print 'Transitions: ' + str(len(T))

print ' **** '

for s in s0:
    print s

print ' **** '

#zstate = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
zstate = np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0])


sstate=(np.array([   1 ,   0,    0,    0,    0,    1 ,   1 ,   1 ,   1 ,   1]))

tr = Transition(zstate,sstate)
print tr.checkValidity()

pos = nx.fruchterman_reingold_layout(G)

print G.selfloop_edges()


for v in G.nodes():
    G.node[v]['state']=v

nx.draw(G, pos)
node_labels = nx.get_node_attributes(G,'state')
nx.draw_networkx_labels(G, pos, labels = node_labels)
#plt.savefig('this.png')
plt.show()


