import numpy as np
from itertools import chain, combinations

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
        print 'what? '+str(x)

class Transition():

    def __init__(self, origin, destination):
        self.transition = destination - origin
        self.origin = origin
        self.destination = destination
        self.numVars = self.transition.shape[0] / 2

    def applyEpsilonOrdering(self):
        copy =  self.origin.copy()
        copy[np.where(copy < -5)] = 0

        # split on interval->point, point->interval
        intervals = copy[val_idx] % 2
        points = 1 - intervals

        update_points = points * copy[delta_idx]

        # split intervals to basis vectors
        eye = np.eye(self.numVars)
        bases = eye[np.where(intervals>0)]
        possible_update_intervals = []

        for combo in chain.from_iterable(combinations(bases, r) for r in range(len(bases) + 1)):
            update = np.zeros(self.numVars)
            for x in list(combo):
                update += x
            possible_update_intervals.append(update)

        copy[val_idx] +=

        # apply influence propagation
        if copy[i]>0 or copy[o]>0:
            if copy[o] == 0:
                if copy[dv] > -5:
                    copy[dv] = min(copy[dv]+1, 1)
                else:
                    copy[dv] = 1
            elif copy[o] > 0 and copy[i]>0:
                copy[dv] = -9
            elif copy[i] == 0:
                copy[dv] = max(copy[dv]-1, -1)

        # apply proportionality propagation
        copy[do]=copy[dh]=copy[dp]=copy[dv]

        return copy


    def prettyprint(self):
        res = '------\n'
        for j in range(len(val_idx)):
            res += d(self.origin[j])+d(self.origin[j+numVars])+'\t'+d(self.transition[j])+d(self.transition[j+numVars])+'\t'+d(self.destination[j])+d(self.destination[j+numVars])+'\n'
        res += '------'
        return res


    def checkValidity(self):

        # debugging
        if str(self.origin) == '[ 0.  1.  1.  1.  1.  0. -1. -1. -1. -1.]':
            if str(self.destination) == '[ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]':
                print 'ah'


        # Local conditions
        # 0. Epsilon ordering: going from a value to an interval should happen immediately
        epsForced = self.applyEpsilonOrdering()
        if not np.array_equal(epsForced, self.origin) and not np.array_equal(epsForced, self.destination):
            print '!!! Invalid by epsilon rule: forced to apply derivative on point->interval: \n%s \n %s \n %s \n -----' % (self.origin, self.transition, self.destination)
            return False, 5
        elif np.array_equal(epsForced, self.destination):
            return True, 0

        # if equal to origin


        ## 1. Delta order rule: only 1 delta in quantity of derivative at a time
        if 2 in np.abs(self.transition):
            print '!!! Invalid by Delta rule: delta_t >= 2. t=%s' % (self.transition)
            return False, 1

        ## 2. A change in value can only be committed after a change in its derivative
        if not(sum(self.transition[delta_idx]) > 0 and sum(self.transition[val_idx]) == 0):
            if np.logical_not(np.array_equal(np.sign(self.origin[delta_idx]), np.sign(self.transition[val_idx]))):
                print '!!! Invalid by delta-propagation: \n%s \n %s \n %s \n -----' % (self.origin, self.transition, self.destination)
                return False, 2


        # Global conditions
        ## 3. Influence propagation: a change in a value in variable V1 should immediately propagate a change
                # in the same direction for the derivatives of all variables in its influence range
        # I+ relations:
        if self.origin[i] > 0 and (np.sign(self.transition[i]) != np.sign(self.destination[dv])):
            print '!!! Invalid by Influence propagation (I+): \n%s \n %s \n %s \n -----' % (self.origin, self.transition, self.destination)
            return False, 3

        # I- relations:
        if self.origin[o] >0 and (np.sign(self.transition[o]) != -np.sign(self.transition[dv])):
            print '!!! Invalid by Influence propagation (I-): \n%s \n %s \n %s \n -----' % (self.origin, self.transition, self.destination)
            return False, 4

        return True, 0