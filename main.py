from dijsktrace import *


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
G, T = create_graph(S, I, P, der_dom)


# Mapping of origin->destination and vice versa
mapping = {}
for trans in T:

    # Store origin
    if str(trans.origin) not in mapping:
        mapping[str(trans.origin)] = {'origin': [], 'destination':[]}
    mapping[str(trans.origin)]['origin'].append(trans)

    # Store destinations
    if str(trans.destination) not in mapping:
        mapping[str(trans.destination)] = {'origin': [], 'destination':[]}
    mapping[str(trans.destination)]['destination'].append(trans)


print '\n\n Mapping of all states and destinations'


S_map = {}

for i,s in enumerate(S):
    key = str(list(s)).replace('.0','.').replace(',','').replace(' ','  ').replace('[','[ ').replace('  -',' -')
    S_map[key] = i


for key in S_map.keys():
    print 'State %d %s' % (S_map[key], key)
    try:
        print 'As origin'
        if mapping[key]['origin']:
            for i in mapping[key]['origin']:
                print '\ttr: %s' % str(compactRepresentation(i.transition))+'    -->      des: %d' % S_map[str(i.destination)]
            print '\n'

        print 'As destination'
        if mapping[key]['destination']:
            for i in mapping[key]['destination']:
                print '\ttr: %s' % str(compactRepresentation(i.transition)) + '    <--      orig: %d' % S_map[str(i.origin)]

    except KeyError as e:
        print 'State not found in transition graph!!'

    print '\n-------------------------------\n'

print ' -----'
origins = Set([])
destinations = Set([])
transitions = Set([])
total = Set([])

for t in T:
    total.add(str(t.origin))
    total.add(str(t.destination))
    transitions.add(str(t.origin)+str(t.transition)+str(t.destination))

    origins.add(str(t.origin))
    destinations.add(str(t.destination))
    #print t.prettyprint()

print 'Total: ' + str(len(total))
print 'Origin: ' + str(len(origins))
print 'Destinations: ' + str(len(destinations))
print 'Transitions: ' + str(len(transitions))

print ' After transition check **** '
i = 0
for s in S:
    print '%d %s' % (i,s)
    i += 1
print ' **** '


print ' Deleted states due to transition checks **** '

strS = [str(x) for x in S]

states = Set(strS)
diff = states - total
for i in range(len(diff)):
    d = diff.pop()
    print '%d: %s'% (i+1, d)
# print ' **** '

pos = nx.circular_layout(G)

print G.selfloop_edges()



print_trace(G, S, 0, 2)


for v in G.nodes():
    G.node[v]['state']=v

nx.draw(G, pos)
node_labels = nx.get_node_attributes(G,'state')
nx.draw_networkx_labels(G, pos, labels = node_labels)
#plt.savefig('this.png')
# plt.show()

# Test case
# #
# zstate = np.array([1, 2, 2, 2, 2, -1, -1, -1 ,-1 ,-1])
# sstate=(np.array([1,1,1,1,1, -1,0,0,0,0]))
#
# tr = Transition(zstate,sstate)
# print checkTransitionValidity(tr, I, P, der_dom)
#

