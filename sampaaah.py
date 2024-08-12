import matplotlib.pyplot as plt
import numpy as np
from math import sin, pi
import time



##for i in x:
##    yi = sin(i)
##    y = np.append(y,yi)
##print(x)
##print(y)
##
##plt.figure(1)
##plt.plot(x,y)
##plt.show()

tend = 10
i = 0
x = np.linspace(0,2*pi,tend)
y = np.array([])
plt.figure(1)
n = 0

while 1:
    time.sleep(0.1)
    xi = x[i]
    yi = sin(xi)
    np.append(y,yi)
    i += 1
    n += 1

    if i > tend-1:
        i = 0
        
    if n > 2*tend-1:
        break

    


