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
        
        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.complex_1.start()

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
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
    
    def __init__(self,a):
        super().__init__()
        self.state = False
        print(self.state)
        self.SP = "1"
        self.PV = "0"
        self.OP = "0"
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
##    def run(self):
##        self.isRunning = True
##        if self.state and self.isRunning:
##            pid_1 = flakes.standard(self.sample_time) #NOTE: 1 = sample_time
##            pid_1.name = 'rfopdt'
##            pid_1.PV = [None,float(self.PV)]
##            pid_1.OP = float(self.OP)
##            pid_1.SP = float(self.SP)
##            while 1:
##                time.sleep(self.sample_time)
##                pid_1.OP, pid_1.PV[0], pid_1.ioe = pid_1.pid(pid_1.SP, pid_1.OP, pid_1.ioe, pid_1.PV,1,1,1)
##                pid_1.PV[-1] = pid_1.systemModel(pid_1._Flakes__model, pid_1.PV[0], pid_1.OP,1,1)
##                self.PV = pid_1.PV[-1]
##                self.OP = pid_1.OP
##                self.signalBack_1.emit(self.SP, self.PV, self.OP)
##                print(pid_1.error)
    def stop(self):
        self.isRunning = False
        self.quit()
        self.terminate()   
                  
    @Slot(dict)
    def dataReceiver(self, param):
        self.SP = param["SP"]
        self.PV = param["PV"]
        self.OP = param["OP"]
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    app.aboutToQuit.connect(window.complex_1.stop)
    sys.exit(app.exec())
