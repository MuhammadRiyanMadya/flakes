#!usr/bin/env python
"""
The module for real-time process control simulator
"""

import numpy as np
import sys
import time

from PySide6.QtWidgets import (QWidget,QApplication, QMainWindow,
                               QGridLayout, QLineEdit, QSpinBox,
                               QGroupBox, QDialog, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout)

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

import pyqtgraph as pg
import functools

from flakes import flakes

class mainWindow(QWidget):
    controlSignal_1 = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP = []
        self.dataPV = []
        self.dataOP = [] #Future: change to numpy array

        #-* Main layout and Widget
        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)

        #-* Wigdet Formation
        self.controller_1 = mainInput('Process Control 1', self)
        self.controller_1.controlConfig()

        self.controller_2 = mainInput('Process Control 2', self)
        self.controller_2.controlConfig()

        self.signal_1 = mainInput('Signal 1', self)

        #-* Layout Allocation
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(self.controller_1,0,0)
        layout.addWidget(self.controller_2,1,0)
        layout.addLayout(self.signal_1.signalConfig(),3,1,2,1)

        #-* Backgroudn Actions
        self.complex_1 = controlComplex(self)
        
        # |-* Intermediete Paramaters Passing 
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1)
        modeCall = functools.partial(self.complex_1.modeCall, self.controller_1.modeButton)


        # |-* Signal Sender
        self.controller_1.SP.returnPressed.connect(setParam_1)
        self.controller_1.PV.returnPressed.connect(setParam_1)
        self.controller_1.OP.returnPressed.connect(setParam_1)
        self.controller_1.modeButton.clicked.connect(modeCall)
        
        # |-* callback - future from graph: PV (MAN) PV,OP(AUTO)
        self.controller_1.SP.setText(str(self.complex_1.SP))
        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(str(self.complex_1.OP))

##        self.controller_1.SP.setText(self.dataSP[-1])
##        self.controller_1.PV.setText(self.dataPV[-1])
##        self.controller_1.OP.setText(self.dataOP[-1])
        
        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.complex_1.start()

##    def setData(self, sp, pv, op:
##        self.dataSP.append(sp)
##        self.dataPV.append(pv)
##        self.dataOP.append(op)
##        print(self.dataSP)
####        self.graphWidget.plot(self.time, self.data) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
####        
####        if self.time[-1] != self.span:
####            self.graphWidget.setXRange(self.time[-1] - self.span, self.time[-1], padding = 0.3)
####            
##        self.graphWidget.setYRange(min(-2, min(self.data)), max(2, max(self.data)), padding = 0.1)
##        return
##        

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"state": self.controller_1.modeButton.text(),"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
            signal.emit(d)
            
    def graphConfig(self):
        self.graphWidget = pg.PlotWidget()
        
        return self.graphWidget


class mainInput(QGroupBox):
    
    def __init__(self, title, parent = None):
        super().__init__(parent)
        self.title = title
        self.labelSP    = None
        self.labelPV    = None
        self.labelOP    = None
        self.modeButton = None
        self.SP         = None
        self.PV         = None
        self.OP         = None
        
    def signalConfig(self):
        bottomLayout = QHBoxLayout()
        self.setCheckable(True)
        self.setChecked(True)
        self.setMinimumHeight(300)
        bottomLayout.addWidget(self)
        
        return bottomLayout

    def controlConfig(self):
        self.setCheckable(True)
        self.setChecked(True)
        
        self.modeButton = QPushButton("Man")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit("2")
        self.PV = QLineEdit("2")
        self.OP = QLineEdit("3")

        layout = QVBoxLayout(self)
        subLayout1 = QHBoxLayout()
        subLayout1.addWidget(self.labelSP)
        subLayout1.addWidget(self.SP)
        
        subLayout2 = QHBoxLayout()
        subLayout2.addWidget(self.labelPV)
        subLayout2.addWidget(self.PV)
        
        subLayout3 = QHBoxLayout()
        subLayout3.addWidget(self.labelOP)
        subLayout3.addWidget(self.OP)
        
        layout.addWidget(self.modeButton)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)

        return self

class controlComplex(QThread):
    signalBack_1 = Signal(float, float, float)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state = False
        self.SP = "1"
        self.PV = "0"
        self.OP = "0"
        self.PVlast = None
        self.sample_time = 1
        self.isRunning = False
        
    def modeCall(self, instance):
        self.state = instance.isChecked()
        if instance.isChecked():
            instance.setText('Auto')
        else:
            instance.setText('Man')
        return self.state
    
    # P and ID controller
    def run(self):
        self.isRunning = True
        while self.isRunning:
            self.state = self.state
            print(self.state)
            pidOne = flakes.standard(self.sample_time) 
            pidOne.name = 'rfopdt'
            pidOne.SP = float(self.SP)
            pidOne.PV = [self.PVlast,float(self.PV)]
            pidOne.OP = float(self.OP)
            i = 0
            while i < 1:
                if self.state == True:
                    i += 1
                    time.sleep(self.sample_time)
                        
                    pidOne.OP, pidOne.PV[0], pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,1,1,0)
                    pidOne.PV[-1] = pidOne.systemModel(pidOne._flakes__model, pidOne.PV[0], pidOne.OP,1,1)
                        
                    self.PV = float(pidOne.PV[-1])
                    self.PVlast = pidOne.PV[0]
                    self.OP = pidOne.OP
                    print(self.OP)
                    self.signalBack_1.emit(self.SP, self.PV, self.OP)
                else:
                    time.sleep(self.sample_time)
                    
                    pidOne.OP, pidOne.PV[0], pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,1,1,0, mode= False)
                    pidOne.PV[-1] = pidOne.systemModel(pidOne._flakes__model, pidOne.PV[0], pidOne.OP,1,1)
                    
                    self.PV = float(pidOne.PV[-1])
                    self.PVlast = pidOne.PV[0]
                    self.OP = pidOne.OP
                    self.state = self.state
                    print(self.OP)         
                    self.signalBack_1.emit(self.SP, self.PV, self.OP)
  
                  
    @Slot(dict)
    def dataReceiver(self, param):
        self.state = param["state"]
        print("signal recv", self.state)
        self.SP = param["SP"]
        print(self.SP)
        self.PV = param["PV"]
        self.OP = param["OP"]
        
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())
