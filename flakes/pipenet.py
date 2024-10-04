import numpy as np
import matplotlib.pyplot as plt

class PumpNet(object):
    def __init__(self, **kwargs):
        pass


class Branch:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
        self.varNum = len(kwargs)
        self.head_loss = np.array([])
        self.flow = np.array([])
    def SysRes(self, flowMax):

        for vr in range(0,flowMax+1):
            i = 0
            static_head = 0
            head_loss_fr = 0
            self.flow = np.append(self.flow,vr)
            for k, v in self.__dict__.items():
                if i < self.varNum:
                    vs = ((vr/3600)/(3.142*v.diameter**2/(4*10**6)))
                    unit_head_loss = (6.815*(vs/v.C)**1.852*(1/(v.diameter/1000))**1.167)
                    head_loss_fr += unit_head_loss*v.quantity
                    
                if i < self.varNum:
                    static_head += v.static
                    
                if i == (self.varNum-1):
                    press_drop_ep = (((vr/3600)/(3.14*(((v.diameter/1000)/2)**2)))**2)/(2*9.81)
                    
                i += 1

            head_loss = head_loss_fr + static_head + press_drop_ep
            self.head_loss = np.append(self.head_loss, head_loss)

        print(self.flow)
        print(self.head_loss)
        
##        i = 0
##        static_head = 0
##        for k, v in self.__dict__.items():
##            if i < self.varNum:
##                vs = ((flowMax/3600)/(3.142*v.diameter**2/(4*10**6)))
##                unit_head_loss = (6.815*(vs/v.C)**1.852*(1/(v.diameter/1000))**1.167)
##                self.head_loss += unit_head_loss*v.quantity
##            if i < self.varNum:
##                static_head += v.static
##            if i == (self.varNum-1):
##                press_drop_ep = (((flowMax/3600)/(3.14*(((v.diameter/1000)/2)**2)))**2)/(2*9.81)
##            i += 1
##        self.head_loss += static_head + press_drop_ep
##        print(self.head_loss)

        
        
class Node:
    def __init__(self):
        self.diameter = None
        self.C = None
        self.quantity = None

node_1 = Node()
node_2 = Node()
node_3 = Node()
node_4 = Node()

node_1.diameter = 128.2
node_1.C = 130
node_1.quantity = 2
node_1.static = 0

node_2.diameter = 102.26
node_2.C = 130
node_2.quantity = 10
node_2.static = 0

node_3.diameter = 62.71
node_3.C = 130
node_3.quantity = 15
node_3.static = 12

node_4.diameter = 35.04
node_4.C = 130
node_4.static = 8
node_4.quantity = 10 


branch_AB = Branch(node_1 = node_1, node_2 = node_2, node_3 = node_3)
branch_AB.SysRes(40)
branch_AC = Branch(node_1 = node_1, node_2 = node_2, node_4 = node_4)
branch_AC.SysRes(40)

def lineIntersect(line_1: tuple, line_2:tuple,):    
    errorTolerance = 0.01
    C = 300
    while 1:
        maxPoint = int(max(max(line_1[0]), max(line_2[0])))
        pointX = np.linspace(0,maxPoint, C*maxPoint)
        for i in pointX:
            yp1 = np.interp(i,line_1[0], line_1[1])
            yp2 = np.interp(i,line_2[0], line_2[1])
            delVal = abs(yp1-yp2)
            if delVal < errorTolerance:
                return (i, min(yp1,yp2))
            else:
                C *= 2
                
xOrd = lineIntersect((branch_AB.flow, branch_AB.head_loss), (branch_AC.flow, branch_AC.head_loss))
print(xOrd)

def globalHead(ordinate, line_1, line_2):
    global_flow = np.array([ordinate[0]])
    global_head = np.array([ordinate[1]])
    maxPoint = min(max(line_1[1]), max(line_2[1]))
    headPoint = np.linspace(ordinate[1], maxPoint,int(maxPoint+1))
    for i in headPoint:
        xp1 = np.interp(i,line_1[1], line_1[0])
        xp2 = np.interp(i,line_2[1], line_2[0])
        print(xp1)
        print(xp2)
        global_flow = np.append(global_flow,(xp1+xp2))
        global_head = np.append(global_head, i)

    print(global_flow, global_head)
    return global_flow, global_head
    

        

    
xs, ys = globalHead(xOrd,(branch_AB.flow, branch_AB.head_loss), (branch_AC.flow, branch_AC.head_loss))

print(xs, ys)
plt.figure(1)
plt.plot(branch_AB.flow, branch_AB.head_loss)
plt.plot(branch_AC.flow, branch_AC.head_loss)
plt.plot(xs,ys)
plt.xlabel('Flow, m3/hour')
plt.ylabel('Head, m')
plt.show()

##node_1.SysRes(flowMax = 40, equation = 'Hazen-William', graph = 'show')
