# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 00:16:56 2023

@author: ssv
"""

#! usr/bin/env python3

"""Module flakes: Emerging process control technology"""

from scipy import integrate, interpolate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class flakes():
    def __init__(self):
        self.period   = 0
        self.name   = 'fopdt'
        self.Kp     = None
        self.taup   = None
        self.thetap = None
        self.t      = []
        self.u      = []
        self.pv     = []
        self.prm0   = []
        
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
        df = pd.DataFrame(dt)
        df = df.transpose()
        df.to_excel('Stepdata_process_2.xlsx',index = False, header = ['Time','Input','Output'])
        
        return dt

    def graph(self,data, show = True ):
        for i in range(1, len(data) + 1):
            plt.figure(i)
            plt.plot(data[0],data[1],label= 'process')
            if show == True:
                plt.show()
                    
    def file(self,
             title,
             bottom_row,
             sheet = 'Sheet1',
             column = 'A:C',
             show: bool = False,
             hdr = 0
             ):
        
        df = pd.read_excel(title, sheet_name = sheet, usecols = column, header = hdr)
        df_np = df.values[:int(bottom_row)]
        self.t = df_np[:,0].tolist()
        self.u = df_np[:,1].tolist()
        self.pv = df_np[:,2].tolist()
        data = [self.t, self.u, self.pv]
        uf = interpolate.interp1d(self.pv, self.t)
        
        op_min = min(self.u)
        op_max = max(self.u)
        op_range = op_max - op_min
        delta_op = []
        for i in range(1,len(self.u)):
            delta_op.append(self.u[-i] - self.u[-i-1])
        delta_op_max = max(delta_op)
        step_index = len(self.u) - 1 - delta_op.index(delta_op_max) - 1
        
        pv_min = min(self.pv)
        pv_max = max(self.pv)
        pv_range = pv_max - pv_min
        pv_avg_bef = sum(self.pv[:step_index+1]) / len(self.pv[:step_index+1])
        if abs(pv_avg_bef - (self.pv[step_index] - self.pv[step_index-1])) > 0.1*pv_range:
            print("Warning: The step data may not be free of disturbances")
            
        Kp0 = pv_range/op_range
        
        for i in range(len(self.pv)):
            if i == len(self.pv)-1:
                break
            elif abs(self.pv[i+1] - self.pv[i]) > pv_avg_bef:
                thetap_index = i + 1
                break
    
        thetap0 = self.t[thetap_index]-self.t[step_index + 1]
        if thetap0 < 0:
            thetap0 = 0
        
        t_63 = uf(self.pv[thetap_index] + 0.63*Kp0*op_range)
        for i in self.t:
            if i > t_63:
                t_63 = i
                break
        taup0 = t_63 - self.t[thetap_index]
        
        self.prm0 = [Kp0, taup0, thetap0]
        
        if show == True:
            self.graph([data[0], data[1]])
        
        return df_np
    
    def foptd_solver(self, prm):
        Kp = prm[0]
        taup = prm[1]
        thetap = prm[2]
        yt = np.zeros(len(self.t))
        yt[0] = self.pv[0] #vt[0]
        uf = interpolate.interp1d(self.t,self.u)
        
        for i in range(len(self.t)-1):
            tstep = [self.t[i], self.t[i+1]]
            y = integrate.odeint(self.__model,yt[i],tstep,args=(uf,Kp,taup,thetap))
            yt[i+1] = y[-1]
            yt[len(self.t)-1] = yt[len(self.t)-2]    
        return yt
    
    def objective(self, prm):
        yt = self.foptd_solver(prm)
        SSE = 0
        for i in range(len(self.t)):
            SSE = SSE + (self.pv[i] - yt[i])**2
        return SSE
    
    def fit(self, eq_name:str , opt_direction: str):
        prm0 = [3, 9, 0]
        if eq_name == 'foptd':
            solution = optimize.minimize(self.objective, prm0 )
            self.prm = solution.x
            if x[2] < 0:
                x[2] = 0
            #yt = self.foptd_solver(prm)
            #SSE = self.objective(eq_name,prm)
        return self.prm

#test file
lc = flakes()
lc.file('Stepdata_process_2.xlsx', bottom_row = 102)
    

#test response
steamer = flakes()
steamer.response(100,{20:30}, 1, 1)

#test 
#lc = flakes()
#lc.file('Stepdata_process_2.xlsx', bottom_row = 102)
#prm = lc.fit('foptd')
