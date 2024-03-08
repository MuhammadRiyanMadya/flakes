
import matplotlib.pyplot as plt
import datetime
import time


#Zhorizont: realtime controller simulation

class Zhorizon():
    def __init__(self):
        self.time = []
        self.var =[]
    def count_sim(self):
        var = 0
        while True:
            var += 1
            self.var.append(var)
            now = datetime.datetime.now()
            self.time.append(now.strftime('%Y,%m,%d,%H,%M,%S.%f'))
            #self.time.append(time.time())
            time.sleep(0.001)
            if var >= 80:
                break

        
FQ_01 = Zhorizon()
FQ_01.count_sim()
fig, ax = plt.subplots(1,1,layout = 'constrained')
ax.plot(FQ_01.time, FQ_01.var)
plt.show()

print(FQ_01.time)

