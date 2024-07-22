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
                               QPushButton, QLabel, QHBoxLayout,
                               QSpinBox)

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

import pyqtgraph as pg
import functools

from flakes import flakes
import time

class mainWindow(QWidget):
    controlSignal_1 = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP     = []
        self.dataPV     = []
        self.dataOP     = []
        print(self.dataOP)
        self.dataTime   = []
        self.span       = 60

        self.updaterPV = None
        self.updaterOP = None
        self.graphicState = False
        print(self.graphicState)
        

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
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(str(self.complex_1.OP))            

##        self.controller_1.SP.setText(self.dataSP[-1])
##        self.controller_1.PV.setText(self.dataPV[-1])
##        self.controller_1.OP.setText(self.dataOP[-1])
        
        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.complex_1.signalBack_1.connect(self.setData)
        self.complex_1.start()
        
    @Slot(float,float, float,float)
    def setData(self, sp, pv, op, n):
        self.dataSP.append(sp)
        self.dataPV.append(pv)
        self.dataOP.append(op)
        self.dataTime.append(n)

        # |-* updater display
        self.updaterPV = round(pv,4)
        self.updaterOP = round(op,4)
        if self.updaterPV == None:
            self.controller_1.PV.setText("BadValue")
            self.controller_1.OP.setText("BadValue")
        else:
            self.controller_1.PV.setText(str(self.updaterPV))
            
##            self.controller_1.OP.setText(str(self.updaterOP))

        # |-* plot
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataSP, pen='#2E2EFE')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataPV, pen='#2EFEF7'))
        self.v2.addItem(pg.PlotCurveItem(self.dataTime, self.dataOP, pen='#2EFE2E'))

        if self.graphicState != True:
            if self.dataTime[-1] != self.span:
                self.v1.setXRange(self.dataTime[-1] - self.span, self.dataTime[-1], padding = 0.3)
                self.v1.setYRange(min(-5, min(self.dataPV), min(self.dataOP)), max(2, max(self.dataPV), max(self.dataOP)), padding = 0.1)
                self.v2.setYRange(min(-5, min(self.dataPV), min(self.dataOP)), max(2, max(self.dataPV), max(self.dataOP)), padding = 0.1)

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"state": self.controller_1.modeButton.text(),"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
            signal.emit(d)
            
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.l = pg.GraphicsLayout()
        self.graph.setCentralWidget(self.l)
        
        #v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
        self.a2.setRange(-5,15)
        self.v2 = pg.ViewBox()
        self.graph.setWindowTitle('Ampere(t)')
        self.graph.show()
        self.l.addItem(self.a2, row = 2, col = 1, rowspan = 1, colspan = 1)
        
        # blank x-axis to alignment
        ax = pg.AxisItem(orientation='bottom')
        ax.setPen('#000000')
        pos = (2,2)
        self.l.addItem(ax, *pos)
        
        #v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.l.addItem(self.p1, row = 2, col = 2, rowspan = 1, colspan = 1)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})

        # Mouse interaction
        self.graph.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        
        #split main viewbox
##        self.p1.axis_left = self.p1.getAxis('left')
##        pos =(0,1)
##        self.l.addItem(self.p1.axis_left, *pos)
        
        #grid
        self.p1.showGrid(x=True, y=True)
        #Link between v1 and v2
        self.l.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        #Axis label
        self.p1.getAxis('left').setLabel('SP, PV', color='#2E2EFE')
        self.a2.setLabel('OP', color='#2EFE2E')
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1.sigResized.connect(self.updateViews)
        self.updateViews()

        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())

        return
    
    def _on_mouse_clicked(self, event):
        self.graphicState = True
        if event.double():
            self.graphicState = False
        return self.graphicState


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
    signalBack_1 = Signal(float, float, float, float)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state = False
        self.SP = "1"
        self.PV = "0"
        self.OP = "0"
        self.PVlast = None
        self.sample_time = 1
        self.isRunning = False
        self.n = 0
        self.startTime = 0
        self.deadTime = 3
        self.bufferOP = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
        print('bufferPV start', self.bufferOP)
        
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
            pidOne = flakes.standard(self.sample_time) 
            pidOne.name = 'rfopdt'
            self.SP = float(self.SP)
            self.PV = float(self.PV)
            self.OP = float(self.OP)
            
            pidOne.SP = self.SP
            pidOne.PV = [self.PVlast,self.PV]
            pidOne.OP = float(self.OP)
            i = 0
            n = self.n
            self.startTime = time.time()
            while i < 1:
                if (self.state == True) or (self.state == 'Auto'):
                    i += 1
                    n += 1
                    self.n = n
                    time.sleep(self.sample_time)
                    
                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,1,1,0) #pidOne.ioe = 0
                    
                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, PVlast, OP,1,1)
                    
                    self.OP = self.bufferOP[-1]
                    self.PV = PVnew
                    self.PVlast = PVlast
                    self.state = self.state

                    self.signalBack_1.emit(self.SP, self.PV, self.OP, self.startTime)

                    # debugging
##                    print(self.SP)
##                    print(self.PV)
##                    print(self.PVlast)
##                    print(self.OP)
##                    print(self.state, end='\n\n')
                    
                elif (self.state == False) or (self.state == 'Man'):
                    i += 1
                    n += 1
                    self.n = n

                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, self.PV, OP,1,1)

                    self.PVlast = self.PV
                    self.PV = PVnew
                    self.state = self.state
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, self.startTime)
                    time.sleep(self.sample_time)
                    

    def stop(self):
        self.isRunning = False
        self.quit()
        self.terminate()
    
    @Slot(dict)
    def dataReceiver(self, param):
        self.state = param["state"]
        self.SP = param["SP"]
        self.PV = param["PV"]
        self.OP = param["OP"]
        
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
            

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = mainWindow()
        window.show()
        app.aboutToQuit.connect(window.complex_1.stop)
        sys.exit(app.exec())
    except KeyboardInterrupt:
        window.complex_1.stop()
