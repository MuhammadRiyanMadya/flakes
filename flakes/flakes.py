#!usr/bin/env python
"""
Created on Tue Oct 31 00:16:56 2023

@author: mrm

Module flakes: Emerging process control technology
"""

from scipy import integrate, interpolate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import optimize
from datetime import datetime
import time

class Flakes():
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
        
    def __model(self,y,t,uf,Kp,taup,**kwargs):
        if self.name == 'fopdt':
            try:
                if (t - thetap) < 0:
                    u = uf(0)
                else:
                    u = uf(t - thetap)
            except:
                u = uf(0)
            dydt = (Kp*u - y)/taup
        elif self.name == 'rfopdt':
            u = uf
            dydt = ((Kp*u - y)/taup)
        
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
            elif abs(self.pv[i+1] - self.pv[i]) > 3*pv_avg_bef:
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
            yt[i+1] = y[1,0]
            yt[len(self.t)-1] = yt[len(self.t)-2]    
        return yt
    
    def objective(self, prm):
        yt = self.foptd_solver(prm)
        SSE = 0
        for i in range(len(self.t)):
            SSE = SSE + (self.pv[i] - yt[i])**2
        return SSE
    
    def fit(self, eq_name:str):
        prm0 = self.prm0
        if eq_name == 'foptd':
            solution = optimize.minimize(self.objective, prm0 )
            self.prm = solution.x
            if self.prm[2] < 0:
                self.prm[2] = 0
            #yt = self.foptd_solver(prm)
            #SSE = self.objective(eq_name,prm)
        return self.prm

class standard(Flakes):
    __counter = 0
    
    def __init__(self, sample_time=1):
        super().__init__()
        standard.__counter   += 1
        self.SP_storage       = []
        self.PV_storage       = []
        self.sample_time      = sample_time
        self.PV               = [None, 0]
        self.SP               = 0
        self.ioe              = 0
        self.Kc               = 0
        self.T1               = 0
        self.T2               = 0
        
    def pid_config(self, SP, PV, sample_time = 1, archive = True):
        if archive == True:
            self.sample_time = sample_time
            _time_point = datetime.now()
            self.t.append(_time_point)
            self.SP_storage.append(SP)
            self.PV_storage(PV)
            time.sleep(sample_time)
            
    def pid (self,
             SP,
             OP,
             ioe,
             PV: list,
             Kc,
             T1,
             T2,
             op_hi   = 100,
             op_lo   = 0,
             mode = True
            ):
    
        self.error = SP - PV[-1]
        dpv = 0
        if mode == True:
            if PV[0] != None:
                dpv = (PV[-1] - PV[0])/self.sample_time
                ioe = ioe + self.error*self.sample_time
            op = OP + Kc*self.error + Kc/T1*ioe - Kc*T2*dpv
            # anti-reset windup protection
            if op > op_hi:
                op = op_hi
                ioe = ioe - self.error*self.sample_time
            elif op < op_lo:
                op = op_lo
                ioe = ioe + self.error*self.sample_time
        else:
            op = OP
            
        return op, PV[-1], ioe
                
    def systemModel(self,
                    fun,
                    PV0,
                    OP,
                    Kp,
                    taup
                   ):
        
        delta_t = [0, self.sample_time]
        yt = integrate.odeint(fun,PV0,delta_t,args=(OP, Kp, taup))
        PV = yt[1,0]
                       
        return PV
    
    def nodeConnect(self, connect: bool):
        try:
            if connect == True:
                while True:
                    self.pid_config(self.SP_storage, self.PV_storage, self.sample_time)
        except KeyboardInterrupt:
            connect = False
            
##    def mode(self, mode: str)
##        if mode == 'auto':
##            auto_start_time = datetime.now()
##            while mode == 'auto':

# test 19 - 07 - 24
##pid1 = standard(sample_time = 1)
##pid1.name = 'rfopdt'
##pid1.PV = [None, 0]
##pid1.OP = 0
##pid1.SP = 1
##while 1:
##    time.sleep(1)
##    pid1.OP, pid1.PV[0], pid1.ioe = pid1.pid(pid1.SP, pid1.OP, pid1.ioe, pid1.PV,1,1,0)
##    pid1.PV[-1] = pid1.systemModel(pid1._Flakes__model, pid1.PV[0], pid1.OP, 1,1)
##    print(pid1.SP)
##    print(pid1.error)
##    print(pid1.PV)

    
         
class predictiveControl():
    def __init__(self):
        pass
    def objective(j):
        for k in range(1,2*P+1):
            if k==1:
                z0 = y[i-P]
            if k<=P:
                if i-P+k<0:
                    j[k] = 0
                else:
                    j[k] = u[i-P+k]
            elif k>P+M:
                j[k] = j[P+M]
            timeProgram = [deltaTimeProgram*(k-1),deltaTimeProgram*(k)]        
            z_out = odeint(processModel,z0,timeProgram,args=(j[k],K,tau))
            z0 = z_out[-1]
            z[k] = z_out[0]
            SetpointProgram[k] = sp[i]
            deltaj = np.zeros(2*P+1)        
            if k>P:
                deltaj[k] = j[k]-j[k-1]
                se[k] = (SetpointProgram[k]-z[k])**2 + 20 * (j[k])**2
        obj = np.sum(se[P+1:])
        return obj



# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 00:16:56 2023

@author: mrm
"""

#! usr/bin/env python3

"""Module flakes: Emerging process control technology"""

from scipy import integrate, interpolate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import optimize
from datetime import datetime
import time

class Flakes():
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
        
    def __model(self,y,t,uf,Kp,taup,**kwargs):
        if self.name == 'fopdt':
            try:
                if (t - thetap) < 0:
                    u = uf(0)
                else:
                    u = uf(t - thetap)
            except:
                u = uf(0)
            dydt = (Kp*u - y)/taup
        elif self.name == 'rfopdt':
            u = uf
            dydt = ((Kp*u - y)/taup)
        
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
            elif abs(self.pv[i+1] - self.pv[i]) > 3*pv_avg_bef:
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
            yt[i+1] = y[1,0]
            yt[len(self.t)-1] = yt[len(self.t)-2]    
        return yt
    
    def objective(self, prm):
        yt = self.foptd_solver(prm)
        SSE = 0
        for i in range(len(self.t)):
            SSE = SSE + (self.pv[i] - yt[i])**2
        return SSE
    
    def fit(self, eq_name:str):
        prm0 = self.prm0
        if eq_name == 'foptd':
            solution = optimize.minimize(self.objective, prm0 )
            self.prm = solution.x
            if self.prm[2] < 0:
                self.prm[2] = 0
            #yt = self.foptd_solver(prm)
            #SSE = self.objective(eq_name,prm)
        return self.prm

class standard(Flakes):
    __counter = 0
    
    def __init__(self, sample_time=1):
        super().__init__()
        standard.__counter   += 1
        self.SP_storage       = []
        self.PV_storage       = []
        self.sample_time      = sample_time
        self.PV               = [None, 0]
        self.SP               = 0
        self.ioe              = 0
        self.Kc               = 0
        self.T1               = 0
        self.T2               = 0
        
    def pid_config(self, SP, PV, sample_time = 1, archive = True):
        if archive == True:
            self.sample_time = sample_time
            _time_point = datetime.now()
            self.t.append(_time_point)
            self.SP_storage.append(SP)
            self.PV_storage(PV)
            time.sleep(sample_time)
            
    def pid (self,
             SP,
             OP,
             ioe,
             PV: list,
             Kc,
             T1,
             T2,
             op_hi   = 100,
             op_lo   = 0,
             mode = True
            ):
    
        self.error = SP - PV[-1]
        dpv = 0
        if mode == True:
            if PV[0] != None:
                dpv = (PV[-1] - PV[0])/self.sample_time
                ioe = ioe + self.error*self.sample_time
            op = OP + Kc*self.error + Kc/T1*ioe - Kc*T2*dpv
            
            # anti-reset windup protection
            if op > op_hi:
                op = op_hi
                ioe = ioe - self.error*self.sample_time
            elif op < op_lo:
                op = op_lo
                ioe = ioe + self.error*self.sample_time
                
        elif mode == False:
            op = OP
            
            
        return op, PV[-1], ioe
                
    def systemModel(self,
                    fun,
                    PV0,
                    OP,
                    Kp,
                    taup
                   ):
        
        delta_t = [0, self.sample_time]
        yt = integrate.odeint(fun,PV0,delta_t,args=(OP, Kp, taup))
        PV = yt[1,0]
                       
        return PV
    
    def nodeConnect(self, connect: bool):
        try:
            if connect == True:
                while True:
                    self.pid_config(self.SP_storage, self.PV_storage, self.sample_time)
        except KeyboardInterrupt:
            connect = False
            
    def shiftBuffer(self,arr, first, second, index = 0):
        
        sizeArr = np.size(arr)
        
        transA = np.append(arr,first)
        matA = np.delete(transA,index)
        transB = np.append(matA,second)
        res = np.delete(transB,index)
        
        sizeRes = np.size(res)
        
        if sizeArr != sizeRes:
            print("Error, numpy array dimension reduced")

        return res
    
            
##    def mode(self, mode: str)
##        if mode == 'auto':
##            auto_start_time = datetime.now()
##            while mode == 'auto':

# test 19 - 07 - 24
##pid1 = standard(sample_time = 1)
##pid1.name = 'rfopdt'
##pid1.PV = [None, 0]
##pid1.OP = 0
##pid1.SP = 1
##while 1:
##    time.sleep(1)
##    pid1.OP, PVpast, pid1.ioe = pid1.pid(pid1.SP, pid1.OP, pid1.ioe, pid1.PV,1,1,0)
##    PVnew = pid1.systemModel(pid1._flakes__model, PVpast, pid1.OP, 1,1)
##    pid1.PV = [PVpast, PVnew]
##    print(pid1.SP)
##    print(pid1.error)
##    print(pid1.PV)

    
         
class predictiveControl():
    def __init__(self):
        pass
    def objective(j):
        for k in range(1,2*P+1):
            if k==1:
                z0 = y[i-P]
            if k<=P:
                if i-P+k<0:
                    j[k] = 0
                else:
                    j[k] = u[i-P+k]
            elif k>P+M:
                j[k] = j[P+M]
            timeProgram = [deltaTimeProgram*(k-1),deltaTimeProgram*(k)]        
            z_out = odeint(processModel,z0,timeProgram,args=(j[k],K,tau))
            z0 = z_out[-1]
            z[k] = z_out[0]
            SetpointProgram[k] = sp[i]
            deltaj = np.zeros(2*P+1)        
            if k>P:
                deltaj[k] = j[k]-j[k-1]
                se[k] = (SetpointProgram[k]-z[k])**2 + 20 * (j[k])**2
        obj = np.sum(se[P+1:])
        return obj
