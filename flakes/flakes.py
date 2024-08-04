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
        self.error            = 0
        
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
    
        self.error = PV[-1] - SP 
        dpv = 0
        if mode == True:
            if PV[0] != None:
                dpv = (PV[-1] - PV[0])/self.sample_time
                ioe = ioe + self.error*self.sample_time
            if T1 != 0:
                op = OP - Kc*self.error + Kc/T1*ioe - Kc*T2*dpv
                
            op = OP - Kc*self.error - Kc*T2*dpv
            
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
            
    def shiftBuffer(self,arr, first, second = None, index = 0):
        
        sizeArr = np.size(arr)
        
        transA = np.append(arr,first)
        res = np.delete(transA,index)
        if second != None:
            transB = np.append(res,second)
            res = np.delete(transB,index)
        
        sizeRes = np.size(res)
                                        
        if sizeArr != sizeRes:
            print("Error, numpy array dimension reduced")

        return res

    def nonLinearGain(self, error, KLIN, NLFM, NLGAIN,divisor=100):
        KNL = NLFM + NLGAIN*(error**2)/divisor
        K = KLIN*KNL
        
        return K
    
    def narrowGain(self, SP, KLIN, KGAP, GAPLO, GAPHI):
        if (PV >= (SP-GAPLO)) or (PV <= (SP-GAPHI)):
            K = KLIN*KGAP
        else:
            K = KLIN
            
        return K
    def externalGain(self, KLIN, KEXT):
        K = KLIN*KEXT
        
        return K
    
            
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
        
    def __timeRoot(self, n):
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

    def timeMaker(self, i, cont = False, nodesNum = 4, timeStart = 0):
        timeNode = __timeRoot(nodesNum)
        if cont:
            Ns = np.array([timeStart])
            for n in range(i):
                Ns = np.append(Ns,timeNode[1:]+n)
            return Ns
        return timeNode+i-1

    # test 1
    def __colloc(self, n):
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

    def __funRoot(self, z, *param):
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

    def collocation(self,
                    fun,
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
##    time = timeMaker(10,cont=True)
##    print(time)
##
##    def __model(y,t,uf,Kp,taup):
##        u = uf
##        dydt = ((Kp*u - y)/taup)
##        return dydt
##
##    ode = odeint(__model,5,list(time), args=(3,1,1))
##    print(ode)
##
##    plt.plot(time, res, color='green', marker='o')
##    plt.plot(time, ode, color='red')
##    plt.show()

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
        self.Kp     = 1
        self.taup   = 1
        self.thetap = 1
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
        self.bufPVoptimizer = np.array([])
        self.bufOPoptimizer = np.array([])
        self.sample_time      = sample_time
        self.PV               = [None, 0]
        self.SP               = 0
        self.OP               = 0
        self.ioe              = 0
        self.Kc               = 0
        self.T1               = 0
        self.T2               = 0
        self.error            = 0
        
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
    
        self.error = PV[-1] - SP 
        dpv = 0
        if mode == True:
            if PV[0] != None:
                dpv = (PV[-1] - PV[0])/self.sample_time
                ioe = ioe + self.error*self.sample_time
            if T1 != 0:
                op = OP - Kc*self.error + Kc/T1*ioe - Kc*T2*dpv
                
            op = OP - Kc*self.error - Kc*T2*dpv
            
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
            
    def shiftBuffer(self,arr, first, second = None, index = 0):
        
        sizeArr = np.size(arr)
        
        transA = np.append(arr,first)
        res = np.delete(transA,index)
        if second != None:
            transB = np.append(res,second)
            res = np.delete(transB,index)
        
        sizeRes = np.size(res)
                                        
        if sizeArr != sizeRes:
            print("Error, numpy array dimension reduced")

        return res

    def nonLinearGain(self, error, KLIN, NLFM, NLGAIN,divisor=100):
        KNL = NLFM + NLGAIN*(error**2)/divisor
        K = KLIN*KNL
        
        return K
    
    def narrowGain(self, SP, KLIN, KGAP, GAPLO, GAPHI):
        if (PV >= (SP-GAPLO)) or (PV <= (SP-GAPHI)):
            K = KLIN*KGAP
        else:
            K = KLIN
            
        return K
    def externalGain(self, KLIN, KEXT):
        K = KLIN*KEXT
        
        return K
    
            
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
         
class optimalControl(standard):
    def __init__(self):
        super().__init__()
        self.pLine          = 1
        self.mLine          = 1
        self.maxmove        = 1


    def objective(self, u):
        """
        The outer variables:
        
        timePoint   : time vector of the actual process
        PV          : process variable
        i           : time point
        OP          : input to the system
        
        """
        for k in range(1,2*self.pLine+1):
            if len(self.bufPVoptimizer) < self.pLine:
                if k == 1:
                    y0 = 0
##                elif k == 1 and IntMan == True:
##                    pass
##                    y0 = float(IntMan.text()) # Input manual the initial for the very first time activation
                if k < self.pLine:
                    if len(self.bufOPoptimizer)-self.pLine+k<0:
                        u[k] = 0
                    else:
                        u[k] = self.bufOPoptimizer[len(self.bufOPoptimizer)-self.pLine+k]
                elif k >= self.pLine + self.mLine:
                    u[k] = self.u0Predicted[self.pLine+self.mLine]
                print()
                print("growing u", u)
                print()
            else:
                if k == 1:
                    y0 = self.bufOPoptimizer[-self.pLine]
                if k < self.pLine:
                    u[k] = self.bufOPoptimizer[len(self.bufOPoptimizer)-self.pLine+k]
                elif k > self.pLine:
                    u[k] = self.u0Predicted[len(self.bufOPoptimizer)]
            print()
            print("fix u", u)
            print()
                    
##            delt = [0, self.sample_time] #Need Att
##            res = self.collocation(self._optimalControl__funRoot, delt, y0, self.u0Predicted[k],self.Kp,self.taup)
##            y0 = res[1,0]
##            self.yPredicted[k] = res[0,0]
##
##            self.SPmvh[k] = self.SP[i]
##            delu = np.zeros(2*self.pLine+1)
##
##            if k>self.pLine:
##                delu[k] = self.u0Predicted[k]-self.u0Predicted[k-1]
##                self.se[k] = (self.SPmvh[k]- self.PV[k])**2 + 20 * (delu[k])**2
##
##            # Sum of Squared Error calculation      
##            self.obj = np.sum(self.se[P+1:])
##            
##        return self.obj
                    
    def mpcActive(self, arrPV, arrOP, pLine, mLine, maxmove, PV, OP):
        self.pLine = pLine
        self.mLine = mLine
        self.maxmove = maxmove
        self.se             = np.zeros(2*self.pLine+1)
        self.u0Predicted    = np.zeros(2*self.pLine+1)
        self.uPredicted     = np.zeros(2*self.pLine+1)
        self.yPredicted     = np.zeros(2*self.pLine+1)
        self.SPmvh          = np.zeros(2*self.pLine+1)
        self.delu           = np.zeros(2*self.pLine+1)
        self.obj            = 0
        
        
        if len(arrPV) < 2*pLine:
            arrPV = np.append(arrPV, PV)
            arrOP = np.append(arrOP, OP)
        else:
            arrPV = self.shiftBuffer(arrPV, PV)
            arrOP = self.shiftBuffer(arrOP, OP)
            
        self.bufPVoptimizer = arrPV
        self.bufOPoptimizer = arrOP
        
        print()
        print("buffer OP", self.bufOPoptimizer)
        print()
            
        self.objective(self.u0Predicted)
        
        
##        solv = optimize.minimize(self.objective, self.u0Predicted, method = 'SLSQP')
##        self.uPredicted = solv.x
##        self.delu = np.diff(self.uPredicted)
##
##        if np.abs(self.delu[self.pLine]) >= maxmove:
##            if self.delu[self.pLine] > 0:
##                self.OP = self.OP + maxmove
##            else:
##                self.OP = self.OP - maxmove
##        else:
##            self.OP = self.OP + self.delu[self.pLine]
##        return self.bufPVoptimizer, self.bufOPoptimizer
        return arrPV, arrOP

    
    def __timeRoot(self, n):
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

    def timeMaker(self, i, cont = False, nodesNum = 4, timeStart = 0):
        timeNode = self._optimalControl__timeRoot(nodesNum)
        if cont:
            Ns = np.array([timeStart])
            for n in range(i):
                Ns = np.append(Ns,timeNode[1:]+n)
            return Ns
        return timeNode+i-1

    # test 1
    def __colloc(self, n):
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
            NC = self.optimalControl__colloc(4)
        return NC

    # test 2
    ##print(__colloc(6))

    def __funRoot(self, z, *param):
        y0      = param[0]
        u       = param[1]
        Kp      = param[2]
        tau     = param[3]
        nodes   = param[4]
        
        y0 = y0
        N  = self._optimalControl__colloc(nodes)
        m = (nodes-1)*2
        y  = z[0:nodes-1]
        dy = z[nodes-1:m]

        F = np.empty(m)
        F[0:nodes-1] = np.dot(N,dy) - (y-y0)
        F[nodes-1:m] = tau*dy + y - Kp*u
        return F

    def collocation(self,
                    fun,
                    time,
                    y0,
                    u,
                    Kp,
                    tau,
                    nodes = 4,
                    ):
        
        zGuess = np.ones((nodes-1)*2)
        res = np.array([y0])
        
        for i in range(1,time+1):
            y0 = y0
            N = np.dot(self._optimalControl__colloc(nodes),i)
            z = optimize.fsolve(fun,zGuess,args=(y0,u,Kp,tau, nodes))
            res = np.append(res,z[0:nodes-1])
            y0 = z[2]
        return res

    # test
##mpc = optimalControl()
##
##time = mpc.timeMaker(10,cont=True)
##print(time)
##
##def __model(y,t,uf,Kp,taup):
##    u = uf
##    dydt = ((Kp*u - y)/taup)
##    return dydt
##
##ode = integrate.odeint(__model,5,list(time), args=(3,1,1))
##print(ode)
##
##res = mpc.collocation(mpc._optimalControl__funRoot,10,5,3,1,1,4)
##plt.plot(time, res, color='green', marker='o')
##plt.plot(time, ode, color='red')
##plt.show()


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
        self.Kp     = 1
        self.taup   = 1
        self.thetap = 1
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
        self.bufPVoptimizer = np.array([])
        self.bufOPoptimizer = np.array([])
        self.sample_time      = sample_time
        self.PV               = [None, 0]
        self.SP               = 0
        self.OP               = 0
        self.ioe              = 0
        self.Kc               = 0
        self.T1               = 0
        self.T2               = 0
        self.error            = 0
        
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
    
        self.error = PV[-1] - SP 
        dpv = 0
        if mode == True:
            if PV[0] != None:
                dpv = (PV[-1] - PV[0])/self.sample_time
                ioe = ioe + self.error*self.sample_time
            if T1 != 0:
                op = OP - Kc*self.error + Kc/T1*ioe - Kc*T2*dpv
                
            op = OP - Kc*self.error - Kc*T2*dpv
            
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
            
    def shiftBuffer(self,arr, first, second = None, index = 0):
        
        sizeArr = np.size(arr)
        
        transA = np.append(arr,first)
        res = np.delete(transA,index)
        if second != None:
            transB = np.append(res,second)
            res = np.delete(transB,index)
        
        sizeRes = np.size(res)
                                        
        if sizeArr != sizeRes:
            print("Error, numpy array dimension reduced")

        return res

    def nonLinearGain(self, error, KLIN, NLFM, NLGAIN,divisor=100):
        KNL = NLFM + NLGAIN*(error**2)/divisor
        K = KLIN*KNL
        
        return K
    
    def narrowGain(self, SP, KLIN, KGAP, GAPLO, GAPHI):
        if (PV >= (SP-GAPLO)) or (PV <= (SP-GAPHI)):
            K = KLIN*KGAP
        else:
            K = KLIN
            
        return K
    def externalGain(self, KLIN, KEXT):
        K = KLIN*KEXT
        
        return K
    
            
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
         
class optimalControl(standard):
    def __init__(self):
        super().__init__()
        self.pLine          = 1
        self.mLine          = 1
        self.maxmove        = 1


    def objective(self, u):
        """
        The outer variables:
        
        timePoint   : time vector of the actual process
        PV          : process variable
        i           : time point
        OP          : input to the system
        
        """
        for k in range(1,2*self.pLine+1):
            if len(self.bufPVoptimizer) < self.pLine:
                if k == 1:
                    y0 = 0
##                elif k == 1 and IntMan == True:
##                    pass
##                    y0 = float(IntMan.text()) # Input manual the initial for the very first time activation
                if k < self.pLine:
                    if len(self.bufOPoptimizer)-self.pLine+k<0:
                        u[k] = 0
                    else:
                        u[k] = self.bufOPoptimizer[len(self.bufOPoptimizer)-self.pLine+k]
                elif k >= self.pLine + self.mLine:
                    u[k] = self.u0Predicted[self.pLine+self.mLine]
            else:
                if k == 1:
                    y0 = self.bufOPoptimizer[-self.pLine]
                if k < self.pLine:
                    u[k] = self.bufOPoptimizer[len(self.bufOPoptimizer)-self.pLine+k]
                elif k > self.pLine:
                    u[k] = self.u0Predicted[len(self.bufOPoptimizer)]
                    
            delt = [0, self.sample_time] #Need Att
            
##            res = self.collocation(self._optimalControl__funRoot, delt, y0, self.u0Predicted[k],self.Kp,self.taup)
##            y0 = res[self.nodes-2]
##            self.yPredicted[k] = res[self.nodes-2]
            
            self.name = 'rfopdt'
            res = integrate.odeint(self._Flakes__model,y0,delt, args=(self.u0Predicted[k],self.Kp, self.taup))
            y0 = res[1,0]
            self.yPredicted[k] = res[0,0]
            
            self.SPmvh[k] = self.SP
            delu = np.zeros(2*self.pLine+1)

            if k>self.pLine:
                delu[k] = self.u0Predicted[k]-self.u0Predicted[k-1]
                self.se[k] = (self.SPmvh[k]- self.PV)**2 + 20 * (delu[k])**2

            # Sum of Squared Error calculation      
            self.obj = np.sum(self.se[self.pLine:])
            
        return self.obj
                    
    def mpcActive(self, arrPV, arrOP, pLine, mLine, maxmove, PV, OP):
        self.pLine = pLine
        self.mLine = mLine
        self.maxmove = maxmove
        self.se             = np.zeros(2*self.pLine+1)
        self.u0Predicted    = np.zeros(2*self.pLine+1)
        self.uPredicted     = np.zeros(2*self.pLine+1)
        self.yPredicted     = np.zeros(2*self.pLine+1)
        self.SPmvh          = np.zeros(2*self.pLine+1)
        self.delu           = np.zeros(2*self.pLine+1)
        self.obj            = 0
        self.nodes          = 4
        
        
        if len(arrPV) < 2*pLine:
            arrPV = np.append(arrPV, PV)
            arrOP = np.append(arrOP, OP)
        else:
            arrPV = self.shiftBuffer(arrPV, PV)
            arrOP = self.shiftBuffer(arrOP, OP)
            
        self.bufPVoptimizer = arrPV
        self.bufOPoptimizer = arrOP
        
        self.objective(self.u0Predicted)
        
        
        solv = optimize.minimize(self.objective, self.u0Predicted, method = 'SLSQP')
        self.uPredicted = solv.x
        self.delu = np.diff(self.uPredicted)

        if np.abs(self.delu[self.pLine-1]) >= maxmove:
            if self.delu[self.pLine-1] > 0:
                OP = OP + maxmove
            else:
                OP = OP - maxmove
        else:
            OP = OP + self.delu[self.pLine-1]
            

        return OP

    
    def __timeRoot(self, n):
        if (n==2):
            tr = np.array([0.0,1.0])
        elif (n==3):
            tr = np.array([0.0,0.5,1.0])
        elif (n==4):
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

    def timeMaker(self, i, cont = False, nodes= 4, timeStart = 0):
        timeNode = self._optimalControl__timeRoot(nodes)
        if cont:
            Ns = np.array([timeStart])
            for n in range(i):
                Ns = np.append(Ns,timeNode[1:]+n)
            return Ns
        return timeNode+i-1

    # test 1
    def __colloc(self, n):
        if (n==2):
            NC = np.array([[1.0]])
        elif (n==3):
            NC = np.array([[0.75, -0.25],
                           [1.00, 0.00]])
        elif (n==4):
            NC = np.array([[0.436,-0.281, 0.121],
                           [0.614, 0.064, 0.0461],
                           [0.603, 0.230, 0.167]])
        elif (n==5):
            NC = np.array([[0.278, -0.202, 0.169, -0.071],
                           [0.398,  0.069, 0.064, -0.031],
                           [0.387,  0.234, 0.278, -0.071],
                           [0.389,  0.222, 0.389,  0.000]])
        elif (n==6):
            NC = np.array([[0.191, -0.147, 0.139, -0.113, 0.047],
                           [0.276,  0.059, 0.051, -0.050, 0.022],
                           [0.267,  0.193, 0.252, -0.114, 0.045],
                           [0.269,  0.178, 0.384,  0.032, 0.019],
                           [0.269,  0.181, 0.374,  0.110, 0.067]])
        else:
            NC = self._optimalControl__colloc(4)
        return NC

    # test 2
    ##print(__colloc(6))

    def __funRoot(self, z, *param):
        y0      = param[0]
        u       = param[1]
        Kp      = param[2]
        tau     = param[3]
        nodes   = param[4]
        
        y0 = y0
        N  = self._optimalControl__colloc(nodes)
        m = (nodes-1)*2
        y  = z[0:nodes-1]
        dy = z[nodes-1:m]

        F = np.empty(m)
        F[0:nodes-1] = np.dot(N,dy) - (y-y0)
        F[nodes-1:m] = tau*dy + y - Kp*u
        return F

    def collocation(self,
                    fun,
                    time,
                    y0,
                    u,
                    Kp,
                    tau,
                    nodes = 4
                    ):
        self.nodes = nodes
        y0 = y0
        zGuess = np.ones((nodes-1)*2)
        res = np.array([y0])
        if type(time) == int or type(time) == float:
            for i in range(1,time+1):
                N = np.dot(self._optimalControl__colloc(nodes),i)
                z = optimize.fsolve(fun,zGuess,args=(y0,u,Kp,tau, nodes), xtol =1e-5 )
                res = np.append(res,z[0:nodes-1])
                y0 = z[2]
            return res
            
        
        if type(time) == list:
            if len(time) == 2:
                if time[1] > time[0]:
                    delt = time[1] - time[0]
                    N = np.dot(self._optimalControl__colloc(nodes), delt)
                    z = optimize.fsolve(fun,zGuess,args=(y0,u,Kp,tau, nodes), xtol =1e-5)
                    return z

# test
##mpc = optimalControl()
##
##time = mpc.timeMaker(10,cont=True, nodes=2)
##print(time)
##
##def __model(y,t,uf,Kp,taup):
##    u = uf
##    dydt = ((Kp*u - y)/taup)
##    return dydt
##
##ode = integrate.odeint(__model,5,list(time), args=(3,1,1))
##print(ode)
##
##
##res = mpc.collocation(mpc._optimalControl__funRoot,10,5,3,1,1,4)
##print(res)
##print(len(res))
##
##y0 = 5
##yp = [y0]
##for i in range(0,10): 
##    delt =[0,1]
##    y = mpc.collocation(mpc._optimalControl__funRoot,delt,y0,3,1,1,nodes=4)
##    yp = np.append(yp,y[mpc.nodes-2])
##    y0 = y[mpc.nodes-2]
##    print(y0)
##
##print("yp", yp)
##print(len(yp))
##    
##plt.plot(time, yp, color='green', marker='o')
##plt.plot(time, ode, color='red')
##plt.show()
