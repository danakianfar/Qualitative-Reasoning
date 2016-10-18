# -*- coding: utf-8 -*-

var_names = [ 'Inflow', 'Volume', 'Height', 'Pressure', 'Outflow']
dom_names = {0: '0', 1 : '+', 2 : 'M'}
der_names = {0: '0', 1 : '⇑', -1 : '⇓', -9 : '?'}

def describe_state(state, state_num, var_names, dom_names, der_names):
    nvars = len(state)/2

    print '* State ' + str(state_num) + ' *'

    for i in range(nvars):
        print var_names[i] + '(' + dom_names[state[i]] + ',' + der_names[state[i + nvars]] + ')'

describe_state([ 1,  2,  1,  1,  1,  1, 0, -1, -1, -9], 1, var_names, dom_names, der_names)
