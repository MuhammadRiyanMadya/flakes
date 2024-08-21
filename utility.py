from flakes import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt


fl  = flakes.disturbance()
FC202A, _ = fl.modelDFile(r"C:\Users\ssv\Documents\MRM\Exp\FC202A.csv")
fl.k = np.array([])
FC202AKeys, _ = fl.modelDFile(r"C:\Users\ssv\Documents\MRM\Exp\FC202AKeys.csv")
                             
mydict = dict(zip(FC202AKeys, FC202A))

od = collections.OrderedDict(sorted(mydict.items()))
del od[0]

for k,v in od.items():
    print(k, "-->", v)

    
plt.plot(od.keys(), od.values())
plt.show()
