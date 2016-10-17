import numpy as np
import itertools

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

print np.shape(S)


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
    print len(del_states)
    # deletes the invalid states
    S = np.delete(S,del_states, axis=0)
    return S

S = prune_states(S)

print np.shape(S)

print S

print '----'

print S[3]

print S[42]

print S[3] - S[42]

print '----'

print S[-6]

print S[-7]

print S[-6] - S[-7]
