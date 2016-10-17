import numpy as np

class Transition():

    def __init__(self, origin, destination):
        self.val = destination - origin
        self.numVars = self.val.shape[0]

    def checkValidity(self):

        # Local conditions
        ## 1. Epsilon order rule: only 1 delta in quantity of derivative at a time
        if len(np.where(np.abs(self.val) == 2)[0]) > 1:
            return False

        ## 2. A change in value can only be committed after a change in its variable
        for i in range(self.val.shape[0]/2):
            if not np.logical_or(self.val[i] ==0 ,self.val[i+self.numVars] == 0):
                return False


        # Global conditions
        ## Influence propagation: a change in a value in variable V1 should immediately propagate a change
                # in the same direction for the derivatives of all variables in its influence range