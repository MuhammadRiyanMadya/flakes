# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:20:50 2024

@author: ssv
"""

import numpy as np
from scipy.optimize import fsolve

def timeMaker(i, cont = False):
    timeRoot = np.array([0, 0.5 - np.sqrt(5)/10, 0.5 + np.sqrt(5)/10, 1])
    if cont:
        Ns = np.array([])
        for n in range(i):
            Ns = np.append(Ns,timeRoot+n)
        return Ns
    return timeRoot+i
# test 1
# print(timeMaker(0))

N = np.array([[0.436,-0.281, 0.121], \
              [0.614, 0.064, 0.0461], \
              [0.603, 0.230, 0.167]])
y0 = 5
zGuess = np.zeros(6) # y1-y3 and dydt1-dydt3
y = np.array([])
# test 2
# print(np.dot(N,0))

def myFunction(z):
    y  = z[0:3]
    dy = z[3:6]

    F = np.empty(6)
    F[0:3] = np.dot(N,dy) - (y-y0)
    F[3:7] = dy + y
    return F

for i in range(1,1):
    N = np.dot(N,i)
    z = fsolve(myFunction,zGuess)
    y = np.append(y,z[0:3])
    y0 = zGuess[2]

# test 3
print(y)
