import numpy as np
import itertools

class Variable:

    def __init__(self, name, domain, val = None):
        self.name = name
        self.value = val
        self.domain = domain
        deriv = Derivative(name+'_der', [-2,-1,0,1])
        self.der = deriv


class Derivative:

    def __init__(self, name, domain, val = None):
        self.name = name
        self.value = val
        self.domain = domain


class State:

    def __init__(self, name, vars):
        self.name = name
        self.vars = vars


# 0, plus, max domain for all the variables
var_dom = [0, 1, 2]

# ?, negative, 0, plus for all derivatives
der_dom = [-2,-1,0,1]

I = Variable('Input', var_dom)
V = Variable('Volume', var_dom)
O = Variable('Outflow', var_dom)
P = Variable('Pressure', var_dom)
H = Variable('Height', var_dom)

vars = [I, V, O, P, H]

st_var = list(itertools.product(var_dom, repeat=len(vars)))
st_der = list(itertools.product(der_dom, repeat=len(vars)))
states = list(itertools.product(st_var, st_der))

S = []

for i in range(len(states)):
    S.append( np.asarray(states[i][0] + states[i][1]))

S = np.asarray(S)