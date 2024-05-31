
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:20:50 2024

@author: ssv
"""

import numpy as np
from scipy.optimize import fsolve

def __timeRoot(n):
    if (n==4):
        tr = np.array([0, 0.5 - np.sqrt(5)/10, 0.5 + np.sqrt(5)/10, 1])
    elif (n==5):
        tr = np.array([0, 0.5 - np.sqrt(21)/14,0.5, 0.5 + np.sqrt(21)/14, 1])
    elif (n==6):
        tr = np.array([0, \
                       0.5 - np.sqrt((7 + 2*np.sqrt(7))/21)/2, \
                       0.5 - np.sqrt((7 - 2*np.sqrt(7))/21)/2, \
                       0.5 + np.sqrt((7 - 2*np.sqrt(7))/21)/2, \
                       0.5 + np.sqrt((7 + 2*np.sqrt(7))/21)/2, \
                       1])
        
    else:
        tr = __timeRoot(4)
    return tr

# test
##print(__timeRoot(0))  

def timeMaker(i, cont = False, tr = 6):
    timeNode = timeRoot(tr)
    if cont:
        Ns = np.array([])
        for n in range(i):
            Ns = np.append(Ns,timeNode+n)
        return Ns
    return timeNode+i

# test 1
##print(timeMaker(4,cont = True))

def __colloc(n):
    if (n==4):
        NC = np.array([[0.436,-0.281, 0.121], \
                       [0.614, 0.064, 0.0461], \
                       [0.603, 0.230, 0.167]])
    elif (n==5):
        NC = np.array([[0.278, -0.202, 0.169, -0.071], \
                       [0.398,  0.069, 0.064, -0.031], \
                       [0.387,  0.234, 0.278, -0.071], \
                       [0.389,  0.222, 0.389,  0.000]])
    elif (n==6):
        NC = np.array([[0.191, -0.147, 0.139, -0.113, 0.047],
                       [0.276,  0.059, 0.051, -0.050, 0.022],
                       [0.267,  0.193, 0.252, -0.114, 0.045],
                       [0.269,  0.178, 0.384,  0.032, 0.019],
                       [0.269,  0.181, 0.374,  0.110, 0.067]])
    else:
        NC = __colloc(4)
    return NC

# test 2
##print(__colloc(6))

def __myFunction(z):
    y0 = 5
    N  = __colloc(4)
    y  = z[0:3]
    dy = z[3:6]

    F = np.empty(6)
    F[0:3] = np.dot(N,dy) - (y-y0)
    F[3:7] = dy + y
    return F

def CLCmethod(period, y0, n):

    y0 = y0
    zGuess = np.ones(6)
    res = np.array([y0])
    
    for i in range(1,period):
        N = np.dot(__colloc(n),i)
        z = fsolve(__myFunction,zGuess)
        res = np.append(res,z[0:3])
        y0 = zGuess[2]
    return res 

# test 3
print(CLCmethod(4,5,4))
