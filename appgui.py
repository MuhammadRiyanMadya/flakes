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
                               QSpinBox, QTabWidget, QSizePolicy,
                               QTableWidget)

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QPalette, QColor

import pyqtgraph as pg
import functools

from flakes import flakes
import time


def embed_hbox_layout(w, margin = 5):
    """ Embed a widget into a layout to givev it a frame"""
    result = QWidget()
    layout = QHBoxLayout(result)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.addWidget(w)
    return result

class mainWindow(QWidget):
    controlSignal_1     = Signal(dict)
    controlConst_1      = Signal(dict)
    modelParam_1        = Signal(dict) 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP     = []
        self.dataPV     = []
        self.dataOP     = []
        self.dataError  = []
        self.errHor     = []
        self.dataTime   = []
        self.span       = 60

        self.updaterPV = None
        self.updaterOP = None
        self.graphicState = False
        

        #-* Main layout and Widget
        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)

        #-* Sub layout
        self.bottomLayout = QHBoxLayout(self)

        #-* Wigdet Formation
        self.controller_1 = mainInput('Process Control 1', self)
        self.controller_1Box = self.controller_1.controlConfig()

        self.controller_2 = mainInput('Process Control 2', self)
        self.controller_2Box = self.controller_2.controlConfig()

        self.intConst_1 = mainInput('Signal 1', self)
        self.intConst_1Box = self.intConst_1.tabBuilder()

        self.intConst_2 = mainInput('Signal 1', self)
        self.intConst_2Box = self.intConst_2.tabBuilder()

        self.intConst_3 = mainInput('Signal 1', self)
        self.intConst_3Box = self.intConst_3.signalConfig()

        self.intConst_4 = mainInput('Signal 1', self)
        self.intConst_4Box = self.intConst_4.signalConfig()

        #-* Layout Allocation

        self.bottomLayout.addWidget(self.intConst_1Box)
        self.bottomLayout.addWidget(self.intConst_2Box)
        self.bottomLayout.addWidget(self.intConst_3Box)
        self.bottomLayout.addWidget(self.intConst_4Box)
        
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(self.controller_1Box,0,0)
        layout.addWidget(self.controller_2Box,1,0)
        layout.addLayout(self.bottomLayout,3,1,2,1)

        #-* Backgroudn Actions
        self.complex_1 = controlComplex(self)
        
        # |-* Intermediete Paramaters Passing 
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1)
        modeCall = functools.partial(self.complex_1.modeCall, self.controller_1.modeButton)
        setConst_1 = functools.partial(self.setConst, self.controlConst_1)
        setModel_1 = functools.partial(self.setModel, self.modelParam_1)


        # |-* Signal Sender
        self.controller_1.SP.returnPressed.connect(setParam_1)
        self.controller_1.PV.returnPressed.connect(setParam_1)
        self.controller_1.OP.returnPressed.connect(setParam_1)
        self.controller_1.modeButton.clicked.connect(modeCall)

        self.intConst_1.K1.returnPressed.connect(setConst_1)
        self.intConst_1.T1.returnPressed.connect(setConst_1)
        self.intConst_1.T2.returnPressed.connect(setConst_1)
        self.intConst_1.KLIN.returnPressed.connect(setConst_1)
        self.intConst_1.KEXT.returnPressed.connect(setConst_1)
        self.intConst_1.KNL.returnPressed.connect(setConst_1)
        self.intConst_1.NLFM.returnPressed.connect(setConst_1)
        self.intConst_1.NLGAIN.returnPressed.connect(setConst_1)
        self.intConst_1.KGAP.returnPressed.connect(setConst_1)
        self.intConst_1.GAPLO.returnPressed.connect(setConst_1)
        self.intConst_1.GAPHI.returnPressed.connect(setConst_1)

        self.intConst_1.Kp.returnPressed.connect(setModel_1)
        self.intConst_1.Tp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.setText(str(self.complex_1.deadTime))
        
        
        # |-* callback - future from graph: PV (MAN) PV,OP(AUTO)
        self.controller_1.SP.setText(self.complex_1.SP)
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(self.complex_1.OP)
        


        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.controlConst_1.connect(self.complex_1.constReceiver)
        self.modelParam_1.connect(self.complex_1.modelReceiver)
        self.complex_1.signalBack_1.connect(self.setData)
        self.complex_1.start()
        
    @Slot(float,float,float,float,float,str)
    def setData(self, sp, pv, op, err, n, sts):
        self.dataSP.append(sp)
        self.dataPV.append(pv)
        self.dataOP.append(op)
        self.dataError.append(round(err,4))
        if err == 0:
            self.errHor.append(0)
        else:
            self.errHor.append(0)    
        self.dataTime.append(n)

        # |-* updater display
        self.updaterPV = round(pv,6)
        self.updaterOP = round(op,6)
        self.updaterState = sts
        
        if self.updaterPV == None:
            self.controller_1.PV.setText("BadValue")
            self.controller_1.OP.setText("BadValue")
        self.controller_1.PV.setText(str(self.updaterPV))
        if self.updaterState == 'True' or self.updaterState == 'Auto':
            self.controller_1.OP.setText(str(self.updaterOP))
        
        # |-* plot
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataSP, pen='#2E2EFE')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataPV, pen='#2EFEF7'))
        self.v2.addItem(pg.PlotCurveItem(self.dataTime, self.dataOP, pen='#FEFE2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.dataError, pen='#FE2E2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.errHor, pen='#962efe'))

        if self.graphicState != True and len(self.dataTime) >= 11:
            if self.dataTime[-1] != self.span:
                self.v1.setXRange(self.dataTime[-1] - self.span, self.dataTime[-1], padding = 0.3)
                self.v1.setYRange(min(-2, min(self.dataPV[-self.span:-1])), max(2, max(self.dataPV[-self.span:-1])), padding = 0.1)
                self.v2.setYRange(min(-2, min(self.dataOP[-self.span:-1])), max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)
                self.v3.setYRange(min(-2, min(self.dataError[-self.span:-1])),max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"state": self.controller_1.modeButton.text(),"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
            signal.emit(d)

    def setConst(self, signal):
        if self.intConst_1.K1.text() !='' or self.intConst_1.T1.text() !='' or self.intConst_1.T2.text() !='':
            d = {"K1": float(self.intConst_1.K1.text()), "T1": float(self.intConst_1.T1.text()), "T2": float(self.intConst_1.T2.text()),
                 "KLIN": float(self.intConst_1.KLIN.text()), "KEXT": float(self.intConst_1.KEXT.text()), "KNL": float(self.intConst_1.KNL.text()),
                 "NLFM": float(self.intConst_1.NLFM.text()), "NLGAIN": float(self.intConst_1.NLGAIN.text()),"KGAP": float(self.intConst_1.KGAP.text()),
                 "GAPLO": float(self.intConst_1.GAPLO.text()), "GAPHI": float(self.intConst_1.GAPHI.text())
                 }
            signal.emit(d) 

    def setModel(self, signal):
        if self.intConst_1.Kp.text() !='' and self.intConst_1.Tp.text() !='' and self.intConst_1.Dp.text() !='':
            d = {"Kp": np.float64(self.intConst_1.Kp.text()), "Tp": np.float64(self.intConst_1.Tp.text()), "Dp": np.float64(self.intConst_1.Dp.text())}
            signal.emit(d)
        
            
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.graph.setWindowTitle('Variables(t)')
        self.graph.show()
        self.l = pg.GraphicsLayout()
        self.graph.setCentralWidget(self.l)
        
        #v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
        self.a2.setRange(-5,15)
        self.v2 = pg.ViewBox()
        self.l.addItem(self.a2, row = 2, col = 2, rowspan = 2, colspan = 1)

        #v2 and a2 for error axis
        self.a3 = pg.AxisItem('left')
        self.a3.setRange(-5,15)
        self.v3 = pg.ViewBox()
        self.l.addItem(self.a3, row = 2, col = 1, rowspan = 2, colspan = 1)
        
        # blank x-axis to alignment
        ax = pg.AxisItem(orientation='bottom')
        ax.setPen('#000000')
        pos = (3,3)
        self.l.addItem(ax, *pos)
        
        #v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.l.addItem(self.p1, row = 2, col = 3, rowspan = 2, colspan = 1)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})

        # Mouse interaction
        self.graph.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        
        #grid
        self.p1.showGrid(x=True, y=True)
        #Link between v1 and v2
        self.l.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        #Link between v3 and v2 ad v1
        self.l.scene().addItem(self.v3)
        self.a3.linkToView(self.v3)
        self.v3.setXLink(self.v1)
        #Axis label
        self.p1.getAxis('left').setLabel('SP, PV', color='#2E2EFE')
        self.a2.setLabel('OP', color='#FEFE2E')
        self.a3.setLabel('Error', color='#FE2E2E')
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1.sigResized.connect(self.updateViews)
        self.updateViews()

        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())
        self.v3.setGeometry(self.v1.sceneBoundingRect())

        return
    
    def _on_mouse_clicked(self, event):
        self.graphicState = True
        if event.double():
            self.graphicState = False
        return self.graphicState


class mainInput(QWidget):
    
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

    def tabBuilder(self):

        result = QTabWidget()
        result.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.group1 = self.signalConfig()
        self.group2 = self.dbConfig()
        result.addTab(embed_hbox_layout(self.group1), "intConst")
        result.addTab(embed_hbox_layout(self.group2), "Distmod")

        return result
        
        
    def signalConfig(self):
##        self.bottomLayout = QHBoxLayout()

        # -- 1
        self.intConstGroup = QGroupBox()
        self.intConstGroup.setCheckable(True)
        self.intConstGroup.setChecked(True)
        self.intConstGroup.setMinimumHeight(300)

        self.labelK1 = QLabel("K1")
        self.K1 = QLineEdit("1")
        self.K1.setFixedWidth(100)
        
        self.labelT1 = QLabel("T1")
        self.T1 = QLineEdit("0")
        self.T1.setFixedWidth(100)
        
        self.labelT2 = QLabel("T2")
        self.T2 = QLineEdit("0")
        self.T2.setFixedWidth(100)
        
        self.labelKLIN = QLabel("KLIN")
        self.KLIN = QLineEdit("0")
        self.KLIN.setFixedWidth(100)

        self.labelKEXT = QLabel("KEXT")
        self.KEXT = QLineEdit("0")
        self.KEXT.setFixedWidth(100)
        
        self.labelKNL = QLabel("KNL")
        self.KNL = QLineEdit("0")
        self.KNL.setFixedWidth(100)
        
        self.labelNLGAIN = QLabel("NLGAIN")
        self.NLGAIN = QLineEdit("0")
        self.NLGAIN.setFixedWidth(100)
        
        self.labelNLFM = QLabel("NLFM")
        self.NLFM = QLineEdit("0")
        self.NLFM.setFixedWidth(100)

        self.labelKGAP = QLabel("KGAP")
        self.KGAP = QLineEdit("0")
        self.KGAP.setFixedWidth(100)
        
        self.labelGAPLO = QLabel("GAPLO")
        self.GAPLO = QLineEdit("0")
        self.GAPLO.setFixedWidth(100)

        self.labelGAPHI = QLabel("GAPHI")
        self.GAPHI = QLineEdit("0")
        self.GAPHI.setFixedWidth(100)

        
        layoutGroup1 = QVBoxLayout(self.intConstGroup)
        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        subLayout4 = QHBoxLayout()
        subLayout5 = QHBoxLayout()
        subLayout6 = QHBoxLayout()
        subLayout7 = QHBoxLayout()
        subLayout8 = QHBoxLayout()
        subLayout9 = QHBoxLayout()
        subLayout10 = QHBoxLayout()
        subLayout11 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelK1)
        subLayout1.addWidget(self.K1)

        subLayout2.addWidget(self.labelT1)
        subLayout2.addWidget(self.T1)

        subLayout3.addWidget(self.labelT2)
        subLayout3.addWidget(self.T2)

        subLayout4.addWidget(self.labelKLIN)
        subLayout4.addWidget(self.KLIN)

        subLayout5.addWidget(self.labelKEXT)
        subLayout5.addWidget(self.KEXT)

        subLayout6.addWidget(self.labelKNL)
        subLayout6.addWidget(self.KNL)

        subLayout7.addWidget(self.labelNLFM)
        subLayout7.addWidget(self.NLFM)
        
        subLayout8.addWidget(self.labelNLGAIN)
        subLayout8.addWidget(self.NLGAIN)

        subLayout9.addWidget(self.labelKGAP)
        subLayout9.addWidget(self.KGAP)

        subLayout10.addWidget(self.labelGAPLO)
        subLayout10.addWidget(self.GAPLO)

        subLayout11.addWidget(self.labelGAPHI)
        subLayout11.addWidget(self.GAPHI)

        
        layoutGroup1.addLayout(subLayout1)
        layoutGroup1.addLayout(subLayout2)
        layoutGroup1.addLayout(subLayout3)
        layoutGroup1.addLayout(subLayout4)
        layoutGroup1.addLayout(subLayout5)
        layoutGroup1.addLayout(subLayout6)
        layoutGroup1.addLayout(subLayout7)
        layoutGroup1.addLayout(subLayout8)
        layoutGroup1.addLayout(subLayout9)
        layoutGroup1.addLayout(subLayout10)
        layoutGroup1.addLayout(subLayout11)
        

        return self.intConstGroup

    def dbConfig(self):
        
        self.dbmodelGroup = QGroupBox()
        self.dbmodelGroup.setCheckable(True)
        self.dbmodelGroup.setChecked(True)
        self.dbmodelGroup.setMinimumHeight(300)
        layout = QVBoxLayout(self.dbmodelGroup)

        self.modelMan = QLabel("Manual Model Changer")
        
        self.labelKp= QLabel("Process Gain")
        self.Kp = QLineEdit("1")
        self.Kp.setFixedWidth(100)
        
        self.labelTp= QLabel("Process Time")
        self.Tp = QLineEdit("1")
        self.Tp.setFixedWidth(100)

        self.labelDp= QLabel("Dead Time")
        self.Dp = QLineEdit("0")
        self.Dp.setFixedWidth(100)
        
        self.modelVar = QLabel("Variance Models")

        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelKp)
        subLayout1.addWidget(self.Kp)

        subLayout2.addWidget(self.labelTp)
        subLayout2.addWidget(self.Tp)

        subLayout3.addWidget(self.labelDp)
        subLayout3.addWidget(self.Dp)

        layout.addWidget(self.modelMan)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)
        layout.addWidget(self.modelVar)
        
        return self.dbmodelGroup

    def controlConfig(self):
        self.controlGroup = QGroupBox()
        self.controlGroup.setCheckable(True)
        self.controlGroup.setChecked(True)
        
        self.modeButton = QPushButton("Man")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit("2")
        self.PV = QLineEdit("2")
        self.OP = QLineEdit("3")

        layout = QVBoxLayout(self.controlGroup)
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

        return self.controlGroup


class controlComplex(QThread):
    signalBack_1 = Signal(float, float, float, float, float, str)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state          = False
        self.SP             = '1'
        self.PV             = '0'
        self.OP             = '0'
        self.PVlast         = None
        self.sample_time    = 1
        self.isRunning      = False
        self.n              = 0
        self.startTime      = 0
        self.deadTime       = 3
        self.bufferOP       = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
        self.K1             = '1'
        self.T1             = '0'
        self.T2             = '0'
        self.KEXT           = '0'
        self.KNL            = '0'
        self.KLIN           = '0'
        self.NLFM           = '0'
        self.NLGAIN         = '0'
        self.KGAP           = '0'
        self.GAPLO          = '0'
        self.GAPHI          = '0'

        self.Kp             = '1'
        self.Tp             = '1'

        
    def modeCall(self, instance):
        self.state = instance.isChecked()
        print(self.state, end='\n\n')
        if instance.isChecked():
            instance.setText('Auto')
        else:
            instance.setText('Man')
        return self.state
    
    # P and ID controller
    def run(self):
        self.isRunning = True
        pidOne = flakes.standard(self.sample_time)
        while self.isRunning:
            self.state = str(self.state)
            pidOne.name = 'rfopdt'
            self.SP = float(self.SP)
            self.PV = float(self.PV)
            self.OP = float(self.OP)
            
            self.Kp = float(self.Kp)
            self.Tp = float(self.Tp)
            
            self.deadTime = round(self.deadTime)
            print('receiver',self.deadTime)
            print('start', self.bufferOP)
            if len(self.bufferOP) < self.deadTime + 1:
                for _ in range((self.deadTime+1) - len(self.bufferOP)):
                    self.bufferOP = np.insert(self.bufferOP,0,self.bufferOP[0])
                    print('add', self.bufferOP)
            if len(self.bufferOP) > self.deadTime + 1:
                print("delta len",len(self.bufferOP) - (self.deadTime+1)) 
                for _ in range(len(self.bufferOP) - (self.deadTime+1)):
                    self.bufferOP = np.delete(self.bufferOP,0)
                    print('less', self.bufferOP)
                    
            self.K1     = float(self.K1)
            self.T1     = float(self.T1)
            self.T2     = float(self.T2)
            self.KLIN   = float(self.KLIN)
            self.KEXT   = float(self.KEXT)
            self.KNL    = float(self.KNL)
            self.NLFM   = float(self.NLFM)
            self.NLGAIN = float(self.NLGAIN)
            self.KGAP   = float(self.KGAP)
            self.GAPLO  = float(self.GAPLO)
            self.GAPHI  = float(self.GAPHI)
            
            
#!()
##            print(self.K1)
##            print(self.T1)
##            print(self.T2)
##            print(self.KLIN)
##            print(self.KEXT)
##            print(self.KNL)
##            print(self.NLFM)
##            print(self.NLGAIN)
##            print(self.KGAP)
##            print(self.GAPLO)
##            print(self.GAPHI)
##            print("model")
##            print(self.Kp)
##            print(self.Tp)
#!()
            
            pidOne.SP = self.SP
            pidOne.PV = [self.PVlast,self.PV]
            pidOne.OP = self.OP
            i = 0
            n = self.n
            self.startTime = time.time()
            while i < 1:
                if (self.state == 'True') or (self.state == 'Auto'):
                    i += 1
                    n += 1
                    self.n = n
                    time.sleep(self.sample_time)

                    # Gain modifier
                    if self.KLIN != 0:
                        if self.KGAP != 0 and (self.GAPLO != 0 or self.GAPHI != 0):
                            self.K1 = pidOne.narrowGain(self.SP, self.PV, self.KLIN, self.KGAP, self.GAPLO, self.GAPHI)

                        if self.NLFM != 0 and self.NLGAIN != 0:
                            self.K1 = pidOne.nonLinearGain(pidOne.error, self.KLIN, self.NLFM, self.NLGAIN) 

#!()
##                    print('After', self.K1)
##                    print()
#!()                    
                    
                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,self.K1,self.T1,self.T2) #pidOne.ioe = 0
                    
                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
                    OP = self.bufferOP[0]
                    
                    # engineering unit - controller to system
##                    OPHI = 100
##                    OPLO = 0
##                    u = OP*(OPHI-OPLO)/100
##                    y = PVlast*(PVEUHI-PVEULO)/100                             
      
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, PVlast, OP, self.Kp, self.Tp)

                    # engineering units settings - system to controller
##                    self.PVEUHI = 100
##                    self.PVEULO = 0
##                    PVnew = ynew/(PVEUHI - PVEULO)
                    
                    self.OP = self.bufferOP[-1]
                    self.PV = PVnew
                    self.PVlast = PVlast
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)

#!()
##                    print(self.SP)
##                    print(self.PV)
##                    print(self.PVlast)
##                    print(self.OP)
##                    print(self.state, end='\n\n')
#!()
                    
                elif (self.state == 'False') or (self.state == 'Man'):
                    i += 1
                    n += 1
                    self.n = n

                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, self.PV, OP, self.Kp, self.Tp)
                    
                    self.PVlast = self.PV
                    self.PV = PVnew
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)
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

    @Slot(dict)
    def constReceiver(self, param):
        self.K1         = param["K1"]
        self.T1         = param["T1"]
        self.T2         = param["T2"]
        self.KLIN       = param["KLIN"]
        self.KEXT       = param["KEXT"]
        self.KNL        = param["KNL"]
        self.NLFM       = param["NLFM"]
        self.NLGAIN     = param["NLGAIN"]
        self.KGAP       = param["KGAP"]
        self.GAPLO      = param["GAPLO"]
        self.GAPHI      = param["GAPHI"]

    @Slot(dict)
    def modelReceiver(self, param):
        self.Kp             = param["Kp"]
        self.Tp             = param["Tp"]
        self.deadTime       = param["Dp"]
        
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
                               QSpinBox, QTabWidget, QSizePolicy,
                               QTableWidget)

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QPalette, QColor

import pyqtgraph as pg
import functools

from flakes import flakes
import time


def embed_hbox_layout(w, margin = 5):
    """ Embed a widget into a layout to givev it a frame"""
    result = QWidget()
    layout = QHBoxLayout(result)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.addWidget(w)
    return result

class mainWindow(QWidget):
    controlSignal_1     = Signal(dict)
    controlConst_1      = Signal(dict)
    modelParam_1        = Signal(dict) 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP     = []
        self.dataPV     = []
        self.dataOP     = []
        self.dataError  = []
        self.errHor     = []
        self.dataTime   = []
        self.span       = 60

        self.updaterPV = None
        self.updaterOP = None
        self.graphicState = False
        

        #-* Main layout and Widget
        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)

        #-* Sub layout
        self.bottomLayout = QHBoxLayout(self)

        #-* Wigdet Formation
        self.controller_1 = mainInput('Process Control 1', self)
        self.controller_1Box = self.controller_1.controlConfig()

        self.controller_2 = mainInput('Process Control 2', self)
        self.controller_2Box = self.controller_2.controlConfig()

        self.intConst_1 = mainInput('Signal 1', self)
        self.intConst_1Box = self.intConst_1.tabBuilder()

        self.intConst_2 = mainInput('Signal 1', self)
        self.intConst_2Box = self.intConst_2.tabBuilder()

        self.intConst_3 = mainInput('Signal 1', self)
        self.intConst_3Box = self.intConst_3.signalConfig()

        self.intConst_4 = mainInput('Signal 1', self)
        self.intConst_4Box = self.intConst_4.signalConfig()

        #-* Layout Allocation

        self.bottomLayout.addWidget(self.intConst_1Box)
        self.bottomLayout.addWidget(self.intConst_2Box)
        self.bottomLayout.addWidget(self.intConst_3Box)
        self.bottomLayout.addWidget(self.intConst_4Box)
        
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(self.controller_1Box,0,0)
        layout.addWidget(self.controller_2Box,1,0)
        layout.addLayout(self.bottomLayout,3,1,2,1)

        #-* Backgroudn Actions
        self.complex_1 = controlComplex(self)
        
        # |-* Intermediete Paramaters Passing 
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1)
        modeCall = functools.partial(self.complex_1.modeCall, self.controller_1.modeButton)
        setConst_1 = functools.partial(self.setConst, self.controlConst_1)
        setModel_1 = functools.partial(self.setModel, self.modelParam_1)


        # |-* Signal Sender
        self.controller_1.SP.returnPressed.connect(setParam_1)
        self.controller_1.PV.returnPressed.connect(setParam_1)
        self.controller_1.OP.returnPressed.connect(setParam_1)
        self.controller_1.modeButton.clicked.connect(modeCall)

        self.intConst_1.K1.returnPressed.connect(setConst_1)
        self.intConst_1.T1.returnPressed.connect(setConst_1)
        self.intConst_1.T2.returnPressed.connect(setConst_1)
        self.intConst_1.KLIN.returnPressed.connect(setConst_1)
        self.intConst_1.KEXT.returnPressed.connect(setConst_1)
        self.intConst_1.KNL.returnPressed.connect(setConst_1)
        self.intConst_1.NLFM.returnPressed.connect(setConst_1)
        self.intConst_1.NLGAIN.returnPressed.connect(setConst_1)
        self.intConst_1.KGAP.returnPressed.connect(setConst_1)
        self.intConst_1.GAPLO.returnPressed.connect(setConst_1)
        self.intConst_1.GAPHI.returnPressed.connect(setConst_1)

        self.intConst_1.Kp.returnPressed.connect(setModel_1)
        self.intConst_1.Tp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.setText(str(self.complex_1.deadTime))
        
        
        # |-* callback - future from graph: PV (MAN) PV,OP(AUTO)
        self.controller_1.SP.setText(self.complex_1.SP)
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(self.complex_1.OP)
        


        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.controlConst_1.connect(self.complex_1.constReceiver)
        self.modelParam_1.connect(self.complex_1.modelReceiver)
        self.complex_1.signalBack_1.connect(self.setData)
        self.complex_1.start()
        
    @Slot(float,float,float,float,float,str)
    def setData(self, sp, pv, op, err, n, sts):
        self.dataSP.append(sp)
        self.dataPV.append(pv)
        self.dataOP.append(op)
        self.dataError.append(round(err,4))
        if err == 0:
            self.errHor.append(0)
        else:
            self.errHor.append(0)    
        self.dataTime.append(n)

        # |-* updater display
        self.updaterPV = round(pv,6)
        self.updaterOP = round(op,6)
        self.updaterState = sts
        
        if self.updaterPV == None:
            self.controller_1.PV.setText("BadValue")
            self.controller_1.OP.setText("BadValue")
        self.controller_1.PV.setText(str(self.updaterPV))
        if self.updaterState == 'True' or self.updaterState == 'Auto':
            self.controller_1.OP.setText(str(self.updaterOP))
        
        # |-* plot
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataSP, pen='#2E2EFE')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataPV, pen='#2EFEF7'))
        self.v2.addItem(pg.PlotCurveItem(self.dataTime, self.dataOP, pen='#FEFE2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.dataError, pen='#FE2E2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.errHor, pen='#962efe'))

        if self.graphicState != True and len(self.dataTime) >= 11:
            if self.dataTime[-1] != self.span:
                self.v1.setXRange(self.dataTime[-1] - self.span, self.dataTime[-1], padding = 0.3)
                self.v1.setYRange(min(-2, min(self.dataPV[-self.span:-1])), max(2, max(self.dataPV[-self.span:-1])), padding = 0.1)
                self.v2.setYRange(min(-2, min(self.dataOP[-self.span:-1])), max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)
                self.v3.setYRange(min(-2, min(self.dataError[-self.span:-1])),max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"state": self.controller_1.modeButton.text(),"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
            signal.emit(d)

    def setConst(self, signal):
        if self.intConst_1.K1.text() !='' or self.intConst_1.T1.text() !='' or self.intConst_1.T2.text() !='':
            d = {"K1": float(self.intConst_1.K1.text()), "T1": float(self.intConst_1.T1.text()), "T2": float(self.intConst_1.T2.text()),
                 "KLIN": float(self.intConst_1.KLIN.text()), "KEXT": float(self.intConst_1.KEXT.text()), "KNL": float(self.intConst_1.KNL.text()),
                 "NLFM": float(self.intConst_1.NLFM.text()), "NLGAIN": float(self.intConst_1.NLGAIN.text()),"KGAP": float(self.intConst_1.KGAP.text()),
                 "GAPLO": float(self.intConst_1.GAPLO.text()), "GAPHI": float(self.intConst_1.GAPHI.text())
                 }
            signal.emit(d) 

    def setModel(self, signal):
        if self.intConst_1.Kp.text() !='' and self.intConst_1.Tp.text() !='' and self.intConst_1.Dp.text() !='':
            d = {"Kp": np.float64(self.intConst_1.Kp.text()), "Tp": np.float64(self.intConst_1.Tp.text()), "Dp": np.float64(self.intConst_1.Dp.text())}
            signal.emit(d)
        
            
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.graph.setWindowTitle('Variables(t)')
        self.graph.show()
        self.l = pg.GraphicsLayout()
        self.graph.setCentralWidget(self.l)
        
        #v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
        self.a2.setRange(-5,15)
        self.v2 = pg.ViewBox()
        self.l.addItem(self.a2, row = 2, col = 2, rowspan = 2, colspan = 1)

        #v2 and a2 for error axis
        self.a3 = pg.AxisItem('left')
        self.a3.setRange(-5,15)
        self.v3 = pg.ViewBox()
        self.l.addItem(self.a3, row = 2, col = 1, rowspan = 2, colspan = 1)
        
        # blank x-axis to alignment
        ax = pg.AxisItem(orientation='bottom')
        ax.setPen('#000000')
        pos = (3,3)
        self.l.addItem(ax, *pos)
        
        #v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.l.addItem(self.p1, row = 2, col = 3, rowspan = 2, colspan = 1)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})

        # Mouse interaction
        self.graph.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        
        #grid
        self.p1.showGrid(x=True, y=True)
        #Link between v1 and v2
        self.l.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        #Link between v3 and v2 ad v1
        self.l.scene().addItem(self.v3)
        self.a3.linkToView(self.v3)
        self.v3.setXLink(self.v1)
        #Axis label
        self.p1.getAxis('left').setLabel('SP, PV', color='#2E2EFE')
        self.a2.setLabel('OP', color='#FEFE2E')
        self.a3.setLabel('Error', color='#FE2E2E')
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1.sigResized.connect(self.updateViews)
        self.updateViews()

        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())
        self.v3.setGeometry(self.v1.sceneBoundingRect())

        return
    
    def _on_mouse_clicked(self, event):
        self.graphicState = True
        if event.double():
            self.graphicState = False
        return self.graphicState


class mainInput(QWidget):
    
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

    def tabBuilder(self):

        result = QTabWidget()
        result.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.group1 = self.signalConfig()
        self.group2 = self.dbConfig()
        result.addTab(embed_hbox_layout(self.group1), "intConst")
        result.addTab(embed_hbox_layout(self.group2), "Distmod")

        return result
        
        
    def signalConfig(self):
##        self.bottomLayout = QHBoxLayout()

        # -- 1
        self.intConstGroup = QGroupBox()
        self.intConstGroup.setCheckable(True)
        self.intConstGroup.setChecked(True)
        self.intConstGroup.setMinimumHeight(300)

        self.labelK1 = QLabel("K1")
        self.K1 = QLineEdit("1")
        self.K1.setFixedWidth(100)
        
        self.labelT1 = QLabel("T1")
        self.T1 = QLineEdit("0")
        self.T1.setFixedWidth(100)
        
        self.labelT2 = QLabel("T2")
        self.T2 = QLineEdit("0")
        self.T2.setFixedWidth(100)
        
        self.labelKLIN = QLabel("KLIN")
        self.KLIN = QLineEdit("0")
        self.KLIN.setFixedWidth(100)

        self.labelKEXT = QLabel("KEXT")
        self.KEXT = QLineEdit("0")
        self.KEXT.setFixedWidth(100)
        
        self.labelKNL = QLabel("KNL")
        self.KNL = QLineEdit("0")
        self.KNL.setFixedWidth(100)
        
        self.labelNLGAIN = QLabel("NLGAIN")
        self.NLGAIN = QLineEdit("0")
        self.NLGAIN.setFixedWidth(100)
        
        self.labelNLFM = QLabel("NLFM")
        self.NLFM = QLineEdit("0")
        self.NLFM.setFixedWidth(100)

        self.labelKGAP = QLabel("KGAP")
        self.KGAP = QLineEdit("0")
        self.KGAP.setFixedWidth(100)
        
        self.labelGAPLO = QLabel("GAPLO")
        self.GAPLO = QLineEdit("0")
        self.GAPLO.setFixedWidth(100)

        self.labelGAPHI = QLabel("GAPHI")
        self.GAPHI = QLineEdit("0")
        self.GAPHI.setFixedWidth(100)

        
        layoutGroup1 = QVBoxLayout(self.intConstGroup)
        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        subLayout4 = QHBoxLayout()
        subLayout5 = QHBoxLayout()
        subLayout6 = QHBoxLayout()
        subLayout7 = QHBoxLayout()
        subLayout8 = QHBoxLayout()
        subLayout9 = QHBoxLayout()
        subLayout10 = QHBoxLayout()
        subLayout11 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelK1)
        subLayout1.addWidget(self.K1)

        subLayout2.addWidget(self.labelT1)
        subLayout2.addWidget(self.T1)

        subLayout3.addWidget(self.labelT2)
        subLayout3.addWidget(self.T2)

        subLayout4.addWidget(self.labelKLIN)
        subLayout4.addWidget(self.KLIN)

        subLayout5.addWidget(self.labelKEXT)
        subLayout5.addWidget(self.KEXT)

        subLayout6.addWidget(self.labelKNL)
        subLayout6.addWidget(self.KNL)

        subLayout7.addWidget(self.labelNLFM)
        subLayout7.addWidget(self.NLFM)
        
        subLayout8.addWidget(self.labelNLGAIN)
        subLayout8.addWidget(self.NLGAIN)

        subLayout9.addWidget(self.labelKGAP)
        subLayout9.addWidget(self.KGAP)

        subLayout10.addWidget(self.labelGAPLO)
        subLayout10.addWidget(self.GAPLO)

        subLayout11.addWidget(self.labelGAPHI)
        subLayout11.addWidget(self.GAPHI)

        
        layoutGroup1.addLayout(subLayout1)
        layoutGroup1.addLayout(subLayout2)
        layoutGroup1.addLayout(subLayout3)
        layoutGroup1.addLayout(subLayout4)
        layoutGroup1.addLayout(subLayout5)
        layoutGroup1.addLayout(subLayout6)
        layoutGroup1.addLayout(subLayout7)
        layoutGroup1.addLayout(subLayout8)
        layoutGroup1.addLayout(subLayout9)
        layoutGroup1.addLayout(subLayout10)
        layoutGroup1.addLayout(subLayout11)
        

        return self.intConstGroup

    def dbConfig(self):
        
        self.dbmodelGroup = QGroupBox()
        self.dbmodelGroup.setCheckable(True)
        self.dbmodelGroup.setChecked(True)
        self.dbmodelGroup.setMinimumHeight(300)
        layout = QVBoxLayout(self.dbmodelGroup)

        self.modelMan = QLabel("Manual Model Changer")
        
        self.labelKp= QLabel("Process Gain")
        self.Kp = QLineEdit("1")
        self.Kp.setFixedWidth(100)
        
        self.labelTp= QLabel("Process Time")
        self.Tp = QLineEdit("1")
        self.Tp.setFixedWidth(100)

        self.labelDp= QLabel("Dead Time")
        self.Dp = QLineEdit("0")
        self.Dp.setFixedWidth(100)
        
        self.modelVar = QLabel("Variance Models")

        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelKp)
        subLayout1.addWidget(self.Kp)

        subLayout2.addWidget(self.labelTp)
        subLayout2.addWidget(self.Tp)

        subLayout3.addWidget(self.labelDp)
        subLayout3.addWidget(self.Dp)

        layout.addWidget(self.modelMan)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)
        layout.addWidget(self.modelVar)
        
        return self.dbmodelGroup

    def controlConfig(self):
        self.controlGroup = QGroupBox()
        self.controlGroup.setCheckable(True)
        self.controlGroup.setChecked(True)
        
        self.modeButton = QPushButton("Man")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit("2")
        self.PV = QLineEdit("2")
        self.OP = QLineEdit("3")

        layout = QVBoxLayout(self.controlGroup)
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

        return self.controlGroup


class controlComplex(QThread):
    signalBack_1 = Signal(float, float, float, float, float, str)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state          = False
        self.SP             = '1'
        self.PV             = '0'
        self.OP             = '0'
        self.PVlast         = None
        self.sample_time    = 1
        self.isRunning      = False
        self.n              = 0
        self.startTime      = 0
        self.deadTime       = 3
        self.bufferOP       = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
        self.K1             = '1'
        self.T1             = '0'
        self.T2             = '0'
        self.KEXT           = '0'
        self.KNL            = '0'
        self.KLIN           = '0'
        self.NLFM           = '0'
        self.NLGAIN         = '0'
        self.KGAP           = '0'
        self.GAPLO          = '0'
        self.GAPHI          = '0'

        self.Kp             = '1'
        self.Tp             = '1'

        self.OPHI           = 100
        self.OPLO           = 0
        self.PVEUHI         = 1
        self.PVEULO         = 0

        
    def modeCall(self, instance):
        self.state = instance.isChecked()
        print(self.state, end='\n\n')
        if instance.isChecked():
            instance.setText('Auto')
        else:
            instance.setText('Man')
        return self.state
    
    # P and ID controller
    def run(self):
        self.isRunning = True
        pidOne = flakes.standard(self.sample_time)
        while self.isRunning:
            self.state = str(self.state)
            pidOne.name = 'rfopdt'
            self.SP = float(self.SP)
            self.PV = float(self.PV)
            self.OP = float(self.OP)
            
            self.Kp = float(self.Kp)
            self.Tp = float(self.Tp)
            
            self.deadTime = round(self.deadTime)
            print('receiver',self.deadTime)
            print('start', self.bufferOP)
            if len(self.bufferOP) < self.deadTime + 1:
                for _ in range((self.deadTime+1) - len(self.bufferOP)):
                    self.bufferOP = np.insert(self.bufferOP,0,self.bufferOP[0])
                    print('add', self.bufferOP)
            if len(self.bufferOP) > self.deadTime + 1:
                print("delta len",len(self.bufferOP) - (self.deadTime+1)) 
                for _ in range(len(self.bufferOP) - (self.deadTime+1)):
                    self.bufferOP = np.delete(self.bufferOP,0)
                    print('less', self.bufferOP)
                    
            self.K1     = float(self.K1)
            self.T1     = float(self.T1)
            self.T2     = float(self.T2)
            self.KLIN   = float(self.KLIN)
            self.KEXT   = float(self.KEXT)
            self.KNL    = float(self.KNL)
            self.NLFM   = float(self.NLFM)
            self.NLGAIN = float(self.NLGAIN)
            self.KGAP   = float(self.KGAP)
            self.GAPLO  = float(self.GAPLO)
            self.GAPHI  = float(self.GAPHI)
            
            
#!()
##            print(self.K1)
##            print(self.T1)
##            print(self.T2)
##            print(self.KLIN)
##            print(self.KEXT)
##            print(self.KNL)
##            print(self.NLFM)
##            print(self.NLGAIN)
##            print(self.KGAP)
##            print(self.GAPLO)
##            print(self.GAPHI)
##            print("model")
##            print(self.Kp)
##            print(self.Tp)
#!()
            
            pidOne.SP = self.SP
            pidOne.PV = [self.PVlast,self.PV]
            pidOne.OP = self.OP
            i = 0
            n = self.n
            self.startTime = time.time()
            while i < 1:
                if (self.state == 'True') or (self.state == 'Auto'):
                    i += 1
                    n += 1
                    self.n = n
                    time.sleep(self.sample_time)
                    
                    # engineering units settings - system to controller
                    pidOne.PV[0] = pidOne.PV[0]/(self.PVEUHI-self.PVEULO)*100
                    pidOne.PV[1] = pidOne.PV[1]/(self.PVEUHI-self.PVEULO)*100
                    pidOne.SP = pidOne.SP/(self.PVEUHI-self.PVEULO)*100

                    # Gain modifier
                    if self.KLIN != 0:
                        if self.KGAP != 0 and (self.GAPLO != 0 or self.GAPHI != 0):
                            self.K1 = pidOne.narrowGain(self.SP, self.PV, self.KLIN, self.KGAP, self.GAPLO, self.GAPHI)

                        if self.NLFM != 0 and self.NLGAIN != 0:
                            self.K1 = pidOne.nonLinearGain(pidOne.error, self.KLIN, self.NLFM, self.NLGAIN) 

#!()
##                    print('After', self.K1)
##                    print()
#!()                    
                    
                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,self.K1,self.T1,self.T2) #pidOne.ioe = 0
                    PVlast = PVlast/100
                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
                    OP = self.bufferOP[0]

#!()
                    print()
                    print("OP controller IN",OP)
                    print("PVlast controller IN", PVlast)
                    print()
#!()

                    # engineering unit - controller to system
                    u = (OP-self.OPLO)*100/(self.OPHI-self.OPLO)
                    self.uDesign = 1
                    u = u/100*self.uDesign
                    y = (PVlast-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
                    self.PVDesign = 1
                    y = y/100*self.PVDesign

#!()
                    print()
                    print("OP system IN",u)
                    print("PV system IN",y)
                    print()
#!()
      
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)

#!()
                    print("PVnew system OUT",PVnew)
#!()
                    # engineering units settings - system to controller
                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
#!()
                    print("PVnew controller OUT",PVnew)
#!()
                    self.OP = self.bufferOP[-1]
                    self.PV = PVnew
                    self.PVlast = PVlast
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)

#!()
##                    print(self.SP)
##                    print(self.PV)
##                    print(self.PVlast)
##                    print(self.OP)
##                    print(self.state, end='\n\n')
#!()
                    
                elif (self.state == 'False') or (self.state == 'Man'):
                    i += 1
                    n += 1
                    self.n = n

                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, self.PV, OP, self.Kp, self.Tp)
                    
                    self.PVlast = self.PV
                    self.PV = PVnew
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)
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

    @Slot(dict)
    def constReceiver(self, param):
        self.K1         = param["K1"]
        self.T1         = param["T1"]
        self.T2         = param["T2"]
        self.KLIN       = param["KLIN"]
        self.KEXT       = param["KEXT"]
        self.KNL        = param["KNL"]
        self.NLFM       = param["NLFM"]
        self.NLGAIN     = param["NLGAIN"]
        self.KGAP       = param["KGAP"]
        self.GAPLO      = param["GAPLO"]
        self.GAPHI      = param["GAPHI"]

    @Slot(dict)
    def modelReceiver(self, param):
        self.Kp             = param["Kp"]
        self.Tp             = param["Tp"]
        self.deadTime       = param["Dp"]
        
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
                               QSpinBox, QTabWidget, QSizePolicy,
                               QTableWidget)

from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QPalette, QColor

import pyqtgraph as pg
import functools

from flakes import flakes
import time


def embed_hbox_layout(w, margin = 5):
    """ Embed a widget into a layout to givev it a frame"""
    result = QWidget()
    layout = QHBoxLayout(result)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.addWidget(w)
    return result

class mainWindow(QWidget):
    controlSignal_1     = Signal(dict)
    controlConst_1      = Signal(dict)
    modelParam_1        = Signal(dict) 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP     = []
        self.dataPV     = []
        self.dataOP     = []
        self.dataError  = []
        self.errHor     = []
        self.dataTime   = []
        self.span       = 60

        self.updaterPV = None
        self.updaterOP = None
        self.graphicState = False
        

        #-* Main layout and Widget
        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)

        #-* Sub layout
        self.bottomLayout = QHBoxLayout(self)

        #-* Wigdet Formation
        self.controller_1 = mainInput('Process Control 1', self)
        self.controller_1Box = self.controller_1.controlConfig()

        self.controller_2 = mainInput('Process Control 2', self)
        self.controller_2Box = self.controller_2.controlConfig()

        self.intConst_1 = mainInput('Signal 1', self)
        self.intConst_1Box = self.intConst_1.tabBuilder()

        self.intConst_2 = mainInput('Signal 1', self)
        self.intConst_2Box = self.intConst_2.tabBuilder()

        self.intConst_3 = mainInput('Signal 1', self)
        self.intConst_3Box = self.intConst_3.signalConfig()

        self.intConst_4 = mainInput('Signal 1', self)
        self.intConst_4Box = self.intConst_4.signalConfig()

        #-* Layout Allocation

        self.bottomLayout.addWidget(self.intConst_1Box)
        self.bottomLayout.addWidget(self.intConst_2Box)
        self.bottomLayout.addWidget(self.intConst_3Box)
        self.bottomLayout.addWidget(self.intConst_4Box)
        
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(self.controller_1Box,0,0)
        layout.addWidget(self.controller_2Box,1,0)
        layout.addLayout(self.bottomLayout,3,1,2,1)

        #-* Backgroudn Actions
        self.complex_1 = controlComplex(self)
        
        # |-* Intermediete Paramaters Passing 
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1)
        modeCall = functools.partial(self.complex_1.modeCall, self.controller_1.modeButton)
        setConst_1 = functools.partial(self.setConst, self.controlConst_1)
        setModel_1 = functools.partial(self.setModel, self.modelParam_1)


        # |-* Signal Sender
        self.controller_1.SP.returnPressed.connect(setParam_1)
        self.controller_1.PV.returnPressed.connect(setParam_1)
        self.controller_1.OP.returnPressed.connect(setParam_1)
        self.controller_1.modeButton.clicked.connect(modeCall)

        self.intConst_1.K1.returnPressed.connect(setConst_1)
        self.intConst_1.T1.returnPressed.connect(setConst_1)
        self.intConst_1.T2.returnPressed.connect(setConst_1)
        self.intConst_1.KLIN.returnPressed.connect(setConst_1)
        self.intConst_1.KEXT.returnPressed.connect(setConst_1)
        self.intConst_1.KNL.returnPressed.connect(setConst_1)
        self.intConst_1.NLFM.returnPressed.connect(setConst_1)
        self.intConst_1.NLGAIN.returnPressed.connect(setConst_1)
        self.intConst_1.KGAP.returnPressed.connect(setConst_1)
        self.intConst_1.GAPLO.returnPressed.connect(setConst_1)
        self.intConst_1.GAPHI.returnPressed.connect(setConst_1)

        self.intConst_1.Kp.returnPressed.connect(setModel_1)
        self.intConst_1.Tp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.setText(str(self.complex_1.deadTime))
        
        
        # |-* callback - future from graph: PV (MAN) PV,OP(AUTO)
        self.controller_1.SP.setText(self.complex_1.SP)
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(self.complex_1.OP)
        


        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.controlConst_1.connect(self.complex_1.constReceiver)
        self.modelParam_1.connect(self.complex_1.modelReceiver)
        self.complex_1.signalBack_1.connect(self.setData)
        self.complex_1.start()
        
    @Slot(float,float,float,float,float,str)
    def setData(self, sp, pv, op, err, n, sts):
        self.dataSP.append(sp)
        self.dataPV.append(pv)
        self.dataOP.append(op)
        self.dataError.append(round(err,4))
        if err == 0:
            self.errHor.append(0)
        else:
            self.errHor.append(0)    
        self.dataTime.append(n)

        # |-* updater display
        self.updaterPV = round(pv,6)
        self.updaterOP = round(op,6)
        self.updaterState = sts
        
        if self.updaterPV == None:
            self.controller_1.PV.setText("BadValue")
            self.controller_1.OP.setText("BadValue")
        self.controller_1.PV.setText(str(self.updaterPV))
        if self.updaterState == 'True' or self.updaterState == 'Auto':
            self.controller_1.OP.setText(str(self.updaterOP))
        
        # |-* plot
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataSP, pen='#2E2EFE')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1.addItem(pg.PlotCurveItem(self.dataTime, self.dataPV, pen='#2EFEF7'))
        self.v2.addItem(pg.PlotCurveItem(self.dataTime, self.dataOP, pen='#FEFE2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.dataError, pen='#FE2E2E'))
        self.v3.addItem(pg.PlotCurveItem(self.dataTime, self.errHor, pen='#962efe'))

        if self.graphicState != True and len(self.dataTime) >= 11:
            if self.dataTime[-1] != self.span:
                self.v1.setXRange(self.dataTime[-1] - self.span, self.dataTime[-1], padding = 0.3)
                self.v1.setYRange(min(-2, min(self.dataPV[-self.span:-1])), max(2, max(self.dataPV[-self.span:-1])), padding = 0.1)
                self.v2.setYRange(min(-2, min(self.dataOP[-self.span:-1])), max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)
                self.v3.setYRange(min(-2, min(self.dataError[-self.span:-1])),max(2, max(self.dataOP[-self.span:-1])), padding = 0.1)

    def setParam(self, signal):
        if self.controller_1.SP.text() !='' and self.controller_1.PV.text() !='' and self.controller_1.OP.text() !='':
            d = {"state": self.controller_1.modeButton.text(),"SP": float(self.controller_1.SP.text()),"PV": float(self.controller_1.PV.text()),"OP": float(self.controller_1.OP.text())} 
            signal.emit(d)

    def setConst(self, signal):
        if self.intConst_1.K1.text() !='' or self.intConst_1.T1.text() !='' or self.intConst_1.T2.text() !='':
            d = {"K1": float(self.intConst_1.K1.text()), "T1": float(self.intConst_1.T1.text()), "T2": float(self.intConst_1.T2.text()),
                 "KLIN": float(self.intConst_1.KLIN.text()), "KEXT": float(self.intConst_1.KEXT.text()), "KNL": float(self.intConst_1.KNL.text()),
                 "NLFM": float(self.intConst_1.NLFM.text()), "NLGAIN": float(self.intConst_1.NLGAIN.text()),"KGAP": float(self.intConst_1.KGAP.text()),
                 "GAPLO": float(self.intConst_1.GAPLO.text()), "GAPHI": float(self.intConst_1.GAPHI.text())
                 }
            signal.emit(d) 

    def setModel(self, signal):
        if self.intConst_1.Kp.text() !='' and self.intConst_1.Tp.text() !='' and self.intConst_1.Dp.text() !='':
            d = {"Kp": np.float64(self.intConst_1.Kp.text()), "Tp": np.float64(self.intConst_1.Tp.text()), "Dp": np.float64(self.intConst_1.Dp.text())}
            signal.emit(d)
        
            
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.graph.setWindowTitle('Variables(t)')
        self.graph.show()
        self.l = pg.GraphicsLayout()
        self.graph.setCentralWidget(self.l)
        
        #v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
        self.a2.setRange(-5,15)
        self.v2 = pg.ViewBox()
        self.l.addItem(self.a2, row = 2, col = 2, rowspan = 2, colspan = 1)

        #v2 and a2 for error axis
        self.a3 = pg.AxisItem('left')
        self.a3.setRange(-5,15)
        self.v3 = pg.ViewBox()
        self.l.addItem(self.a3, row = 2, col = 1, rowspan = 2, colspan = 1)
        
        # blank x-axis to alignment
        ax = pg.AxisItem(orientation='bottom')
        ax.setPen('#000000')
        pos = (3,3)
        self.l.addItem(ax, *pos)
        
        #v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.l.addItem(self.p1, row = 2, col = 3, rowspan = 2, colspan = 1)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})

        # Mouse interaction
        self.graph.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        
        #grid
        self.p1.showGrid(x=True, y=True)
        #Link between v1 and v2
        self.l.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        #Link between v3 and v2 ad v1
        self.l.scene().addItem(self.v3)
        self.a3.linkToView(self.v3)
        self.v3.setXLink(self.v1)
        #Axis label
        self.p1.getAxis('left').setLabel('SP, PV', color='#2E2EFE')
        self.a2.setLabel('OP', color='#FEFE2E')
        self.a3.setLabel('Error', color='#FE2E2E')
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1.sigResized.connect(self.updateViews)
        self.updateViews()

        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())
        self.v3.setGeometry(self.v1.sceneBoundingRect())

        return
    
    def _on_mouse_clicked(self, event):
        self.graphicState = True
        if event.double():
            self.graphicState = False
        return self.graphicState


class mainInput(QWidget):
    
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

    def tabBuilder(self):

        result = QTabWidget()
        result.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.group1 = self.signalConfig()
        self.group2 = self.dbConfig()
        result.addTab(embed_hbox_layout(self.group1), "intConst")
        result.addTab(embed_hbox_layout(self.group2), "Distmod")

        return result
        
        
    def signalConfig(self):
##        self.bottomLayout = QHBoxLayout()

        # -- 1
        self.intConstGroup = QGroupBox()
        self.intConstGroup.setCheckable(True)
        self.intConstGroup.setChecked(True)
        self.intConstGroup.setMinimumHeight(300)

        self.labelK1 = QLabel("K1")
        self.K1 = QLineEdit("1")
        self.K1.setFixedWidth(100)
        
        self.labelT1 = QLabel("T1")
        self.T1 = QLineEdit("0")
        self.T1.setFixedWidth(100)
        
        self.labelT2 = QLabel("T2")
        self.T2 = QLineEdit("0")
        self.T2.setFixedWidth(100)
        
        self.labelKLIN = QLabel("KLIN")
        self.KLIN = QLineEdit("0")
        self.KLIN.setFixedWidth(100)

        self.labelKEXT = QLabel("KEXT")
        self.KEXT = QLineEdit("0")
        self.KEXT.setFixedWidth(100)
        
        self.labelKNL = QLabel("KNL")
        self.KNL = QLineEdit("0")
        self.KNL.setFixedWidth(100)
        
        self.labelNLGAIN = QLabel("NLGAIN")
        self.NLGAIN = QLineEdit("0")
        self.NLGAIN.setFixedWidth(100)
        
        self.labelNLFM = QLabel("NLFM")
        self.NLFM = QLineEdit("0")
        self.NLFM.setFixedWidth(100)

        self.labelKGAP = QLabel("KGAP")
        self.KGAP = QLineEdit("0")
        self.KGAP.setFixedWidth(100)
        
        self.labelGAPLO = QLabel("GAPLO")
        self.GAPLO = QLineEdit("0")
        self.GAPLO.setFixedWidth(100)

        self.labelGAPHI = QLabel("GAPHI")
        self.GAPHI = QLineEdit("0")
        self.GAPHI.setFixedWidth(100)

        
        layoutGroup1 = QVBoxLayout(self.intConstGroup)
        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        subLayout4 = QHBoxLayout()
        subLayout5 = QHBoxLayout()
        subLayout6 = QHBoxLayout()
        subLayout7 = QHBoxLayout()
        subLayout8 = QHBoxLayout()
        subLayout9 = QHBoxLayout()
        subLayout10 = QHBoxLayout()
        subLayout11 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelK1)
        subLayout1.addWidget(self.K1)

        subLayout2.addWidget(self.labelT1)
        subLayout2.addWidget(self.T1)

        subLayout3.addWidget(self.labelT2)
        subLayout3.addWidget(self.T2)

        subLayout4.addWidget(self.labelKLIN)
        subLayout4.addWidget(self.KLIN)

        subLayout5.addWidget(self.labelKEXT)
        subLayout5.addWidget(self.KEXT)

        subLayout6.addWidget(self.labelKNL)
        subLayout6.addWidget(self.KNL)

        subLayout7.addWidget(self.labelNLFM)
        subLayout7.addWidget(self.NLFM)
        
        subLayout8.addWidget(self.labelNLGAIN)
        subLayout8.addWidget(self.NLGAIN)

        subLayout9.addWidget(self.labelKGAP)
        subLayout9.addWidget(self.KGAP)

        subLayout10.addWidget(self.labelGAPLO)
        subLayout10.addWidget(self.GAPLO)

        subLayout11.addWidget(self.labelGAPHI)
        subLayout11.addWidget(self.GAPHI)

        
        layoutGroup1.addLayout(subLayout1)
        layoutGroup1.addLayout(subLayout2)
        layoutGroup1.addLayout(subLayout3)
        layoutGroup1.addLayout(subLayout4)
        layoutGroup1.addLayout(subLayout5)
        layoutGroup1.addLayout(subLayout6)
        layoutGroup1.addLayout(subLayout7)
        layoutGroup1.addLayout(subLayout8)
        layoutGroup1.addLayout(subLayout9)
        layoutGroup1.addLayout(subLayout10)
        layoutGroup1.addLayout(subLayout11)
        

        return self.intConstGroup

    def dbConfig(self):
        
        self.dbmodelGroup = QGroupBox()
        self.dbmodelGroup.setCheckable(True)
        self.dbmodelGroup.setChecked(True)
        self.dbmodelGroup.setMinimumHeight(300)
        layout = QVBoxLayout(self.dbmodelGroup)

        self.modelMan = QLabel("Manual Model Changer")
        
        self.labelKp= QLabel("Process Gain")
        self.Kp = QLineEdit("1")
        self.Kp.setFixedWidth(100)
        
        self.labelTp= QLabel("Process Time")
        self.Tp = QLineEdit("1")
        self.Tp.setFixedWidth(100)

        self.labelDp= QLabel("Dead Time")
        self.Dp = QLineEdit("0")
        self.Dp.setFixedWidth(100)
        
        self.modelVar = QLabel("Variance Models")

        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
        subLayout3 = QHBoxLayout()
        
        subLayout1.addWidget(self.labelKp)
        subLayout1.addWidget(self.Kp)

        subLayout2.addWidget(self.labelTp)
        subLayout2.addWidget(self.Tp)

        subLayout3.addWidget(self.labelDp)
        subLayout3.addWidget(self.Dp)

        layout.addWidget(self.modelMan)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)
        layout.addWidget(self.modelVar)
        
        return self.dbmodelGroup

    def controlConfig(self):
        self.controlGroup = QGroupBox()
        self.controlGroup.setCheckable(True)
        self.controlGroup.setChecked(True)
        
        self.modeButton = QPushButton("Man")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit("2")
        self.PV = QLineEdit("2")
        self.OP = QLineEdit("3")

        layout = QVBoxLayout(self.controlGroup)
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

        return self.controlGroup


class controlComplex(QThread):
    signalBack_1 = Signal(float, float, float, float, float, str)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state          = False
        self.SP             = '1'
        self.PV             = '0'
        self.OP             = '0'
        self.PVlast         = None
        self.sample_time    = 1
        self.isRunning      = False
        self.n              = 0
        self.startTime      = 0
        self.deadTime       = 0
        self.bufferOP       = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
        self.K1             = '1'
        self.T1             = '0'
        self.T2             = '0'
        self.KEXT           = '0'
        self.KNL            = '0'
        self.KLIN           = '0'
        self.NLFM           = '0'
        self.NLGAIN         = '0'
        self.KGAP           = '0'
        self.GAPLO          = '0'
        self.GAPHI          = '0'

        self.Kp             = '1'
        self.Tp             = '1'

        self.OPEUHI           = 100
        self.OPEULO           = 0
        self.PVEUHI         = 2
        self.PVEULO         = 0

        
    def modeCall(self, instance):
        self.state = instance.isChecked()
        print(self.state, end='\n\n')
        if instance.isChecked():
            instance.setText('Auto')
        else:
            instance.setText('Man')
        return self.state
    
    # P and ID controller
    def run(self):
        self.isRunning = True
        pidOne = flakes.standard(self.sample_time)
        while self.isRunning:
            # signal updater  
            self.state = str(self.state)
            pidOne.name = 'rfopdt'
            self.SP = float(self.SP)
            self.PV = float(self.PV)
            self.OP = float(self.OP)
            
            self.Kp = float(self.Kp)
            self.Tp = float(self.Tp)
            self.deadTime = round(self.deadTime)
            print('receiver',self.deadTime)
            print('start', self.bufferOP)
            if len(self.bufferOP) < self.deadTime + 1:
                for _ in range((self.deadTime+1) - len(self.bufferOP)):
                    self.bufferOP = np.insert(self.bufferOP,0,self.bufferOP[0])
                    print('add', self.bufferOP)
            if len(self.bufferOP) > self.deadTime + 1:
                print("delta len",len(self.bufferOP) - (self.deadTime+1)) 
                for _ in range(len(self.bufferOP) - (self.deadTime+1)):
                    self.bufferOP = np.delete(self.bufferOP,0)
                    print('less', self.bufferOP)
                    
            self.K1     = float(self.K1)
            self.T1     = float(self.T1)
            self.T2     = float(self.T2)
            self.KLIN   = float(self.KLIN)
            self.KEXT   = float(self.KEXT)
            self.KNL    = float(self.KNL)
            self.NLFM   = float(self.NLFM)
            self.NLGAIN = float(self.NLGAIN)
            self.KGAP   = float(self.KGAP)
            self.GAPLO  = float(self.GAPLO)
            self.GAPHI  = float(self.GAPHI)
            
            
#!()
##            print(self.K1)
##            print(self.T1)
##            print(self.T2)
##            print(self.KLIN)
##            print(self.KEXT)
##            print(self.KNL)
##            print(self.NLFM)
##            print(self.NLGAIN)
##            print(self.KGAP)
##            print(self.GAPLO)
##            print(self.GAPHI)
##            print("model")
##            print(self.Kp)
##            print(self.Tp)
#!()
            # signal container
            pidOne.SP = self.SP
            pidOne.PV = [self.PVlast,self.PV]
            print("first time", pidOne.PV)
            pidOne.OP = self.OP

            # loop utility
            i = 0
            n = self.n
            self.startTime = time.time()
            while i < 1:
                if (self.state == 'True') or (self.state == 'Auto'):
                    i += 1
                    n += 1
                    self.n = n
                    time.sleep(self.sample_time)
                    
                    # engineering units settings - system to controller
                    pidOne.PV[0] = pidOne.PV[0]*100
                    pidOne.PV[1] = pidOne.PV[1]*100
                    pidOne.SP = pidOne.SP/(self.PVEUHI-self.PVEULO)*100

#!()
                    print()
                    print("pidOne.PV", pidOne.PV)
                    print("pidOne.SP", pidOne.SP)
                    print()
#!()


                    # Gain modifier
                    if self.KLIN != 0:
                        if self.KGAP != 0 and (self.GAPLO != 0 or self.GAPHI != 0):
                            self.K1 = pidOne.narrowGain(pidOne.SP, pidOne.PV, self.KLIN, self.KGAP, self.GAPLO, self.GAPHI)

                        if self.NLFM != 0 and self.NLGAIN != 0:
                            self.K1 = pidOne.nonLinearGain(pidOne.error, self.KLIN, self.NLFM, self.NLGAIN) 

#!()
##                    print('After', self.K1)
##                    print()
#!()                    
                    
                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,self.K1,self.T1,self.T2) #pidOne.ioe = 0
                    PVlast = PVlast/100
                    
                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
                    OP = self.bufferOP[0]

#!()
                    print()
                    print("OP controller IN",OP)
                    print("PVlast controller IN", PVlast)
                    print()
#!()

                    # engineering unit - controller to system
                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
                    self.uDesign = 1
                    u = u/100*self.uDesign
                    y = (PVlast-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
                    self.PVDesign = 1
                    y = y/100*self.PVDesign

#!()
                    print()
                    print("OP system IN",u)
                    print("PV system IN",y)
                    print()
#!()
      
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)

#!()
                    print("PVnew system OUT",PVnew)
#!()
                    # engineering units settings - system to controller
                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
#!()
                    print("PVnew controller OUT",PVnew)
#!()
                    self.OP = self.bufferOP[-1]
                    self.PV = PVnew
                    self.PVlast = PVlast
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)

#!()
##                    print(self.SP)
##                    print(self.PV)
##                    print(self.PVlast)
##                    print(self.OP)
##                    print(self.state, end='\n\n')
#!()
                    
                elif (self.state == 'False') or (self.state == 'Man'):
                    i += 1
                    n += 1
                    self.n = n

                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
#!()
                    print()
                    print("OP controller IN",OP)
                    print("PVlast controller IN", self.PV)
                    print()
#!()

                    # engineering unit - controller to system
                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
                    self.uDesign = 1
                    u = u/100*self.uDesign
                    y = (self.PV-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
                    self.PVDesign = 1
                    y = y/100*self.PVDesign

#!()
                    print()
                    print("OP system IN",u)
                    print("PV system IN",y)
                    print()
#!()
                    
                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)

                    #!()
                    print("PVnew system OUT",PVnew)
#!()
                    # engineering units settings - system to controller
                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
#!()
                    print("PVnew controller OUT",PVnew)
#!()
                    
                    self.PVlast = self.PV
                    self.PV = PVnew
                    self.state = self.state
                    
                    self.signalBack_1.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)
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

    @Slot(dict)
    def constReceiver(self, param):
        self.K1         = param["K1"]
        self.T1         = param["T1"]
        self.T2         = param["T2"]
        self.KLIN       = param["KLIN"]
        self.KEXT       = param["KEXT"]
        self.KNL        = param["KNL"]
        self.NLFM       = param["NLFM"]
        self.NLGAIN     = param["NLGAIN"]
        self.KGAP       = param["KGAP"]
        self.GAPLO      = param["GAPLO"]
        self.GAPHI      = param["GAPHI"]

    @Slot(dict)
    def modelReceiver(self, param):
        self.Kp             = param["Kp"]
        self.Tp             = param["Tp"]
        self.deadTime       = param["Dp"]
        
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



