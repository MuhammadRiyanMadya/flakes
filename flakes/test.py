# test the source code

# %% test response generator

steamer = flakes()
##steamer.response(100,{5:2, 10:1,14:3,20:30,25:29,26:28,30:31}, 4.5, 4, thetap = 10)

#print(steamer.u)
#print(steamer.pv)

# model graph
##fig, ax = plt.subplots(2,1,layout = 'constrained')
##ax[0].plot(steamer.t, steamer.u, 'b',label='input(t)',linewidth=1)
##ax[0].set_ylabel('Unit')
##ax[0].grid(True)
##ax[0].set_title("Step Test of a Process")
##ax[0].legend()
##
##ax[1].plot(steamer.t, steamer.pv, 'r', label='output(t)/process variable(t)',linewidth=1)
##ax[1].set_ylabel('Unit')
##ax[1].set_xlabel('Time')
##ax[1].grid(True)
##ax[1].legend()
##plt.show()
            
# test fitting
levelctrl = flakes()
levelctrl.file('Stepdata_process_2.xlsx', bottom_row = 102)
prm = levelctrl.fit('foptd')        

print(levelctrl.t)
print(levelctrl.prm)
# test helper    
pv = levelctrl.foptd_solver(levelctrl.prm)
pv2 = levelctrl.foptd_solver(levelctrl.prm0)

fig, ax = plt.subplots(1,1,layout='constrained')
ax.plot(levelctrl.t, levelctrl.pv,'yo',label='actual response')
ax.plot(levelctrl.t, pv2,'r--',label='preliminary foptd model')
ax.plot(levelctrl.t, pv,'b-',label='optimized foptd model')
ax.text(-1.9,122,'Detected System = FOPTD')
ax.text(-1.9,115,'Identified FOPTD parameters')
ax.text(-1.9,108,f'Process Gain: {prm[0]}')
ax.text(-1.9,101,f'Process Time: {prm[1]}')
ax.text(-1.9,94,f'Time Delay: {prm[2]}')
ax.set_title('System Modeler')
ax.legend()
plt.show()
