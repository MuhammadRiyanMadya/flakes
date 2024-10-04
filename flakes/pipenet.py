class PumpNet(object):
    def __init__(self, **kwargs):
        pass



class Branch:
    def __init__(self,*args):
        self.args[1] = args[1]

class Node:
    def __init__(self):
        self.diameter = None
        self.C = None
        self.quantity = None

node_1 = Node()
node_2 = Node()
node_3 = Node()

node_1.diameter = 128.2
node_1.C = 130
node_1.quantity = 2
node_2.diameter = 102.26
node_2.C = 130
node_2.quantity = 10
node_3.diameter = 62.71
node_3.C = 130
node_3.quantity = 15


https://www.linkedin.com/pulse/estimating-flow-pipe-branches-multi-branched-pumping-system-nilanjan/
https://www.cibsejournal.com/cpd/modules/2021-08-pro/
https://codingnomads.com/python-object-composition-example
branch_AB = Branch(node_1, node_2, node_3)
branch_AB.node_1.diameter = 120

##node_1.SysRes(flowMax = 40, equation = 'Hazen-William', graph = 'show')

