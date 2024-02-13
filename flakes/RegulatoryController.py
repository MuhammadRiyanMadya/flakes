class RegControl:
    def __init__(self,
                 K      = 1,
                 T1     = 0,
                 T2     = 0,
                 Mode   = 'Auto',
                 Native = 'Direct',
                 Arwnet = 'Active',
                 op_hi  = 100,
                 op_lo  = 0,
                 cv_hi  = 100,
                 cv_lo  = 0,
                 sp_hi  = 0,
                 sp_lo  = 0                 
                 ):
        self.K = K
        self.T1 = T1
        self.T2 = T2
    def pid(self,SP, PV):
        ie0 = 0
        error = SP - PV
        P = self.K*error
        ie = ie0 + error*dt
        I = (self.K/self.T1)*ie
        op = ubias + P + I
        return op
    
# Note: class instantiated by giving PID tuning constants
LevelController = RegControl(K = 1,T1 = 2,T2 = 2)
print(LevelController.pid(1,0))

def level_dynamic(h,t,OP):
    A = 2
    Rv = 0.5
    dhdt = (1/Rv*OP - h)/(A/Rv)
    return dhdt

### time frame
##t_start = 0
##t_end = 100
##t = np.linspace(0,t_end,t_end+1)
##delta_t = t[1]-t[0]
### initial conditions
##PV0 = 20 
##OP0 = 10
### variable frame
##SP = np.ones(t_end+1)*20
##SP[30:60] = 15
##SP[60:] = 25
##PV = np.empty(t_end+1)
##PV[0] = PV0
##OP = np.empty(t_end+1)
##OP[0] = OP0
##error = np.ones(t_end+1)
##P = np.empty(t_end+1)
##I = np.zeros(t_end+1)
##I[0] = 0

# check the frame

##for i in range(0,t_end-1)
##    SP = SP[i]
##    PV = PV[i]
##    OP = LevelController.pid(SP,PV)
##    PV[i+1] = LevelDynamicModel.firstorder(OP)
