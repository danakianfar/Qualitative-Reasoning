import numpy as np
import matplotlib.pyplot as plt
import itertools
from state_graph import *
from sets import Set
from dijsktrace import *

import array

def_max = 2
def_zero = 0
def_plus = 1
def_neg = -1
def_amb = -9

def get_graph():

    return None

def get_full_envisionment(varDomain, derDomain, numOfVars):
    # Variable ordering
    vars = ['I', 'V', 'H', 'P', 'O']

    # creates full envisionment by doing a cross product of possible variables and possible derivatives
    st_var = list(itertools.product(*varDomain))
    st_der = list(itertools.product(*derDomain))
    states = list(itertools.product(st_var, st_der))

    # Cast envisionment to Numpy array
    S = []
    for i in range(len(states)):
        S.append(states[i][0] + states[i][1])
    return np.asarray(S)



## ============================
#  Initialization
## ============================

# Number of variables
numOfVars = 5

var_names = [ 'Inflow', 'Volume', 'Height', 'Pressure', 'Outflow']
dom_names = {0: 'zero', 1 : 'positive', 2 : 'maximum'}
der_names = {0: 'steady', 1 : 'positive', -1 : 'negative', -9 : 'ambiguous'}

# 0, plus, max domain for all the variables
var_dom = [[0.0, 1.0, 2.0],]*numOfVars

# ?, negative, 0, plus for all derivatives
der_dom =    [[-1, 0, 1],
             [-9, -1, 0, 1],
             [-9, -1, 0, 1],
             [-9, -1, 0, 1],
             [-9, -1, 0, 1]]


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


# Get all possible combinations of states and derivatives
S = get_full_envisionment(varDomain=var_dom, derDomain=der_dom, numOfVars=5)

# Get all valid states
S = prune_states(S,I)

# print S

# Create graph with all possible valid transition between the states
G, T = create_graph(S)


print ' -----'
origins = Set([])
destinations = Set([])
total = Set([])

for t in T:
    total.add(str(t.origin))
    total.add(str(t.destination))

    origins.add(str(t.origin))
    destinations.add(str(t.destination))
    #print t.prettyprint()

print 'Total: ' + str(len(total))
print 'Origin: ' + str(len(origins))
print 'Destinations: ' + str(len(destinations))
print 'Transitions: ' + str(len(T))

print ' After transition check **** '
for s in total:
    print s
print ' **** '


print ' Deleted states due to transition checks **** '

strS = [str(x) for x in S]

states = Set(strS)
diff = states - total
for i in range(len(diff)):
    print '%d: %s'% (i+1,diff.pop())
print ' **** '

#zstate = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
zstate = np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0])


sstate=(np.array([   1 ,   0,    0,    0,    0,    1 ,   1 ,   1 ,   1 ,   1]))

tr = Transition(zstate,sstate)
print tr.checkValidity()

pos = nx.fruchterman_reingold_layout(G)

print G.selfloop_edges()



print_trace(G, S, 0, 2)


for v in G.nodes():
    G.node[v]['state']=v

nx.draw(G, pos)
node_labels = nx.get_node_attributes(G,'state')
nx.draw_networkx_labels(G, pos, labels = node_labels)
#plt.savefig('this.png')
plt.show()


