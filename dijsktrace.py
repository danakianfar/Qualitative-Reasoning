# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import itertools
from state_graph import *
import networkx as nx
from transition import Transition

var_names = [ 'I', 'V', 'H', 'P', 'O']
dom_names = {0: '0', 1 : '+', 2 : 'M'}
der_names = {0: '0', 1 : '⇑', -1 : '⇓', -9 : '?'}

def describe_state(state, state_num, var_names, dom_names, der_names, label = ''):
    nvars = len(state)/2

    print '* ' + label + ' State ' + str(state_num) + ' *'

    for i in range(nvars):
        print var_names[i] + '(' + dom_names[state[i]] + ',' + der_names[state[i + nvars]] + ')'

    print ''

def describe_transition(trans, var_names, dom_names, der_names):

    orig = trans.origin
    dest = trans.destination
    trt = trans.transition

    nvars = len(orig) / 2

    if sum(abs(trt)) != 0:
        print '* Transition *'

    for i in range(nvars):
        if trt[i] != 0:
            print var_names[i] + ': ' + dom_names[orig[i]] + ' ↦ ' + dom_names[dest[i]]
        if trt[i + nvars] != 0:
            print 'δ'+ var_names[i] + ': ' + der_names[orig[i + nvars]] + ' ↦ ' + der_names[dest[i + nvars]]

    if sum(abs(trt)) != 0:
        print ''


def print_trace(G, S, s1, s2):
    tr_list = nx.dijkstra_path(G, s1, s2)

    describe_state(S[tr_list[0]], s1, var_names, dom_names, der_names, 'Initial')

    for i in range(1, len(tr_list)):
        istate = S[tr_list[i - 1]]
        fstate = S[tr_list[i]]

        tr = Transition(istate, fstate)

        describe_transition(tr, var_names, dom_names, der_names)

        label = ''
        if tr_list[i] == s2:
            label = 'Final'

        describe_state(fstate, tr_list[i], var_names, dom_names, der_names, label)

istate = np.array([0, 0, 0, 0, 0, 0, -9, 0, 0, 0])
fstate=(np.array([0,0,0,0,0,1,0,0-1,0,0]))

describe_state(istate, 1, var_names, dom_names, der_names)

tr = Transition(istate,fstate)
describe_transition(tr, var_names, dom_names, der_names)

describe_state(fstate, 2, var_names, dom_names, der_names)
