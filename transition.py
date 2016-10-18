import numpy as np

val_idx = range(5)
delta_idx = range(5, 10)
numVars = len(val_idx)
i = 0
v = 1
h = 2
p = 3
o = 4
di = 5
dv = 6
dh = 7
dp = 8
do = 9

def d(x):
    if x == 0:
        return '0'
    elif x == 1:
        return '+'
    elif x == 2:
        return 'm'
    elif x == -1:
        return '-'
    elif x < -5 or x > 5:
        return '?'
    else:
        print 'what: '+str(x)

class Transition():

    def __init__(self, origin, destination):
        self.transition = destination - origin
        self.origin = origin
        self.destination = destination
        self.numVars = self.transition.shape[0] / 2


    def prettyprint(self):
        res = '------\n'
        for j in range(len(val_idx)):
            res += d(self.origin[j])+d(self.origin[j+numVars])+'\t'+d(self.transition[j])+d(self.transition[j+numVars])+'\t'+d(self.destination[j])+d(self.destination[j+numVars])+'\n'
        res += '------'
        return res


    def checkValidity(self):

        # Local conditions
        ## 1. Epsilon order rule: only 1 delta in quantity of derivative at a time
        if 2 in np.abs(self.transition):
            print '!!! Invalid by epsilon rule: delta_t >= 2. t=%s' % (self.transition)
            return False

        ## 2. A change in value can only be committed after a change in its derivative
        if not(sum(self.transition[delta_idx]) > 0 and sum(self.transition[val_idx]) == 0):
            if np.logical_not(np.array_equal(np.sign(self.origin[delta_idx]), np.sign(self.transition[val_idx]))):
                print '!!! Invalid by delta-propagation: %s' % self.prettyprint()
                return False


        # Global conditions
        ## 3. Influence propagation: a change in a value in variable V1 should immediately propagate a change
                # in the same direction for the derivatives of all variables in its influence range
        # I+ relations:
        if self.origin[i] > 0 and (np.sign(self.transition[i]) != np.sign(self.destination[dv])):
            print '!!! Invalid by Influence propagation (I+): %s' % self.prettyprint()
            return False

        # I- relations:
        if self.origin[o] >0 and (np.sign(self.transition[o]) != -np.sign(self.destination[dv])):
            print '!!! Invalid by Influence propagation (I-): %s' % self.prettyprint()
            return False

        return True