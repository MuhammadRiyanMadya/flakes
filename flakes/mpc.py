
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:20:50 2024

@author: ssv
"""

import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from scipy.integrate import odeint

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

## test
##print(__timeRoot(0))  

def timeMaker(i, cont = False, nodesNum = 4, timeStart = 0):
    timeNode = __timeRoot(nodesNum)
    if cont:
        Ns = np.array([timeStart])
        for n in range(i):
            Ns = np.append(Ns,timeNode[1:]+n)
        return Ns
    return timeNode+i-1

# test 1
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

def __funRoot(z, *param):
    y0      = param[0]
    u       = param[1]
    Kp      = param[2]
    tau     = param[3]
    nodes   = param[4]
    
    y0 = y0
    N  = __colloc(nodes)
    m = (nodes-1)*2
    y  = z[0:nodes-1]
    dy = z[nodes-1:m]

    F = np.empty(m)
    F[0:nodes-1] = np.dot(N,dy) - (y-y0)
    F[nodes-1:m] = tau*dy + y - Kp*u
    return F

def collocation(fun,
                time,
                y0,
                u,
                Kp,
                tau,
                nodes,
                ):
    
    zGuess = np.ones((nodes-1)*2)
    res = np.array([y0])
    
    for i in range(1,time+1):
        y0 = y0
        N = np.dot(__colloc(nodes),i)
        z = fsolve(fun,zGuess,args=(y0,u,Kp,tau, nodes))
        res = np.append(res,z[0:nodes-1])
        y0 = z[2]
    return res

# test
k = 1
t = 0.3
u = 0
for i in range(20):
    k +=0.3
    t += 0.4
    u += 1
    res = collocation(__funRoot,10,i,3,1,1,4)
    
print(res)
print(type(res))
time = timeMaker(10,cont=True)
print(time)

def __model(y,t,uf,Kp,taup):
    u = uf
    dydt = ((Kp*u - y)/taup)
    return dydt

ode = odeint(__model,5,list(time), args=(3,1,1))
print(ode)

plt.plot(time, res, color='green', marker='o')
plt.plot(time, ode, color='red')
plt.show()
