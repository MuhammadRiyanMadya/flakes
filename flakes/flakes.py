#! usr/bin/env python3

"""Module flakes: Emerging process control technology"""

from scipy import integrate, interpolate
import matplotlib.pyplot as plt
import pandas as pd

class flakes():
    def __init__(self):
        self.period   = 0
        self.name   = 'fopdt'
        self.Kp     = None
        self.taup   = None
        self.thetap = None
        self.t      = []
        self.u      = []
        self.pv     = None
        
    def __model(self,y,t,uf,Kp,taup,thetap):

        if self.name == 'fopdt':
            try:
                if (t - thetap) < 0:
                    u = uf(0)
                else:
                    u = uf(t - thetap)
            except:
                u = uf(0)
            dydt = (Kp*u - y)/taup
            return dydt
        
    def __timepoint(self, period, time0 = 0):
        
        self.period = period
        for i in range(time0, self.period + 1):
                self.t.append(i)      
        return 
    
    def __steppoint(self, myinput:dict , input0):
        sig = []
        for i in range(0,len(self.t)):
            sig.append(input0)
            
        for keys,values in myinput.items():
            for n in range(keys,len(sig)):
                sig[n]= values
                
        if len(sig) == 0:
            print("The input change for the system is empty. \
The time period must be defined first")
        return sig
        
    def response(self,
                 period     :int,
                 step       :dict,
                 Kp         :int,
                 taup       :int,
                 thetap     :int = 0,
                 IV         :int = 0,
                 input0     :int = 0,
                 time0      :int = 0,
                 filename   :str = 'Step_Data_1',
                 save       :bool = False
                 ):
        
        self.period = period
        self.Kp = Kp
        self.taup = taup
        self.thetap = thetap
        self.__timepoint(self.period, time0)
        self.u = self.__steppoint(step, input0)
        uf = interpolate.interp1d(self.t,self.u)
        self.pv = [IV]
        
        for i in range(0,self.period + 1):
            if i < 1:
                delta_t = [0,1]
            else:
                delta_t = [self.t[i-1],self.t[i]]
            yt = integrate.odeint(self.__model,self.pv[i],delta_t,args=(uf,self.Kp,self.taup,self.thetap))
            self.pv.append(yt[1,0])

        del self.pv[0]
        dt = [self.t, self.u, self.pv]

        return dt

    def graph(self,data, show = True ):
        for i in range(1, len(data) + 1):
            plt.figure(i)
            plt.plot(data[0],data[1],label= 'process')
            if show == True:
                plt.show()
                    
    def file(self,
             title,
             sheet,
             column,
             bottom_row,
             show: bool = True,
             hdr = 0
             ):
                
        df = pd.read_excel(title, sheet_name = sheet, usecols = column,header = hdr)
        df_np = df.values[:int(bottom_row)]
        self.t = df_np[:,0]
        self.u = df_np[:,1]
        self.pv = df_np[:,2]
        data = [self.t, self.u, self.pv]
        if show == True:
            self.graph([data[0], data[1]])
            self.graph([data[0], data[2]])
        
        return df_np
    def pid(self,
            sp: dict,
            Kc: int,
            Tc: int,
            Td: int = 0,
            arwnet: bool = False,
            sp0 = 0,
           ):
        sp = self.__steppoint(sp, sp0)
        for i in range(0,len(self.t)):
            e = self.pv[i] - sp[i]
            
        return op 
            


#test
steamer = flakes()
steamer.response(100,{20:30}, 1, 1)
#print(steamer.u)
#print(steamer.pv)
