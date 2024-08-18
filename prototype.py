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

    controlSignal_2     = Signal(dict)
    controlConst_2      = Signal(dict)
    modelParam_2        = Signal(dict)

    PVCon               = Signal(bool)
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")
        self.dataSP             = []
        self.dataPV             = []
        self.dataOP             = []
        self.dataError          = []
        self.errHor             = []
        self.dataTime           = []
        self.span               = 60
        self.updaterPV          = None
        self.updaterOP          = None
        self.graphicState       = False

        self.dataSP_2           = []
        self.dataPV_2           = []
        self.dataOP_2           = []
        self.dataError_2        = []
        self.errHor_2           = []
        self.dataTime_2         = []
        self.span_2             = 60

        self.updaterPV_2        = None
        self.updaterOP_2        = None
        self.graphicState_2     = False
        

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
        self.controller_2Box = self.controller_2.controlConfig(casButtonAdd = True)

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
        self.complex_1.uConnected = False
        self.complex_1.Kp = 2400
        self.complex_1.PVDesign = 6000
        self.complex_1.PVEUHI = 5000
        self.complex_1.PVEULO = 0
        
        
        self.complex_2 = controlComplex(self)
        self.complex_2.dexpansion = 3
        self.complex_2.sample_time = 1
        self.complex_2.DBActivated  = True
        self.complex_2.dbmodel, self.complex_2.dblength = self.complex_2.DB.modelDFile(r'C:\Users\mrm\Downloads\MMR\Aptcon\Flakes\dtbnmodel.csv')


        # |-* Intermediete Paramaters Passing 
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1, self.controller_1)
        modeCall = functools.partial(self.complex_1.modeCall, self.controller_1.modeButton)
        setConst_1 = functools.partial(self.setConst, self.controlConst_1, self.intConst_1)
        setModel_1 = functools.partial(self.setModel, self.modelParam_1, self.intConst_1)


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
        self.intConst_1.K1.setText(str(self.complex_1.K1))
        self.intConst_1.T1.setText(str(self.complex_1.T1))
        self.intConst_1.T2.setText(str(self.complex_1.T2))
        self.intConst_1.KLIN.setText(str(self.complex_1.KLIN))
        self.intConst_1.KEXT.setText(str(self.complex_1.KEXT))
        self.intConst_1.KNL.setText(str(self.complex_1.KNL))
        self.intConst_1.NLFM.setText(str(self.complex_1.NLFM))
        self.intConst_1.NLGAIN.setText(str(self.complex_1.NLGAIN))
        self.intConst_1.KGAP.setText(str(self.complex_1.KGAP))
        self.intConst_1.GAPHI.setText(str(self.complex_1.GAPHI))
        self.intConst_1.GAPLO.setText(str(self.complex_1.GAPLO))

        self.intConst_1.Kp.returnPressed.connect(setModel_1)
        self.intConst_1.Tp.returnPressed.connect(setModel_1)
        self.intConst_1.Dp.returnPressed.connect(setModel_1)
        self.intConst_1.Kp.setText(str(self.complex_1.Kp))
        self.intConst_1.Tp.setText(str(self.complex_1.Tp))
        self.intConst_1.Dp.setText(str(self.complex_1.deadTime))
        
        
        # |-* callback - future from graph: PV (MAN) PV,OP(AUTO)
        self.controller_1.SP.setText(str(self.complex_1.SP))
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_1.OP.setText(str(self.complex_1.OP))

        # |-* Intermediete Paramaters Passing 
        setParam_2 = functools.partial(self.setParam, self.controlSignal_2, self.controller_2)
        modeCall = functools.partial(self.complex_2.modeCall, self.controller_2.modeButton)
        casCall = functools.partial(self.complex_2.casCall, self.controller_2.casButton)
        setConst_2 = functools.partial(self.setConst, self.controlConst_2, self.intConst_2)
        setModel_2 = functools.partial(self.setModel, self.modelParam_2, self.intConst_2)

##        setCas_2 = functools.partial(self.complex_1.cascadeRec, self.complex_1)

        
        self.intConst_2.K1.returnPressed.connect(setConst_2)
        self.intConst_2.T1.returnPressed.connect(setConst_2)
        self.intConst_2.T2.returnPressed.connect(setConst_2)
        self.intConst_2.KLIN.returnPressed.connect(setConst_2)
        self.intConst_2.KEXT.returnPressed.connect(setConst_2)
        self.intConst_2.KNL.returnPressed.connect(setConst_2)
        self.intConst_2.NLFM.returnPressed.connect(setConst_2)
        self.intConst_2.NLGAIN.returnPressed.connect(setConst_2)
        self.intConst_2.KGAP.returnPressed.connect(setConst_2)
        self.intConst_2.GAPLO.returnPressed.connect(setConst_2)
        self.intConst_2.GAPHI.returnPressed.connect(setConst_2)
        self.intConst_2.K1.setText(str(self.complex_2.K1))
        self.intConst_2.T1.setText(str(self.complex_2.T1))
        self.intConst_2.T2.setText(str(self.complex_2.T2))
        self.intConst_2.KLIN.setText(str(self.complex_2.KLIN))
        self.intConst_2.KEXT.setText(str(self.complex_2.KEXT))
        self.intConst_2.KNL.setText(str(self.complex_2.KNL))
        self.intConst_2.NLFM.setText(str(self.complex_2.NLFM))
        self.intConst_2.NLGAIN.setText(str(self.complex_2.NLGAIN))
        self.intConst_2.KGAP.setText(str(self.complex_2.KGAP))
        self.intConst_2.GAPHI.setText(str(self.complex_2.GAPHI))
        self.intConst_2.GAPLO.setText(str(self.complex_2.GAPLO))

        self.intConst_2.Kp.returnPressed.connect(setModel_2)
        self.intConst_2.Tp.returnPressed.connect(setModel_2)
        self.intConst_2.Dp.returnPressed.connect(setModel_2)
        self.intConst_2.Kp.setText(str(self.complex_2.Kp))
        self.intConst_2.Tp.setText(str(self.complex_2.Tp))
        self.intConst_2.Dp.setText(str(self.complex_2.deadTime))
        # |-* Signal Sender
        self.controller_2.SP.returnPressed.connect(setParam_2)
        self.controller_2.PV.returnPressed.connect(setParam_2)
        self.controller_2.OP.returnPressed.connect(setParam_2)
        self.controller_2.modeButton.clicked.connect(modeCall)
        self.controller_2.casButton.clicked.connect(casCall)

        self.controller_2.SP.setText(str(self.complex_2.SP))
##        self.controller_1.PV.setText(str(self.complex_1.PV))
        self.controller_2.OP.setText(str(self.complex_2.OP))

        self.controlSignal_1.connect(self.complex_1.dataReceiver)
        self.controlConst_1.connect(self.complex_1.constReceiver)
        self.modelParam_1.connect(self.complex_1.modelReceiver)
        self.complex_1.signalBack_1.connect(self.setData)
        self.complex_1.signalBack_1.connect(self.complex_2.cascadeRecv)
        self.complex_1.start()

        self.controlSignal_2.connect(self.complex_2.dataReceiver)
        self.controlConst_2.connect(self.complex_2.constReceiver)
        self.modelParam_2.connect(self.complex_2.modelReceiver)
        self.complex_2.signalBack_1.connect(self.setDataTwo)
        self.complex_2.signalBack_1.connect(self.complex_1.cascadeRecv)
        self.complex_2.start()

        
    @Slot(float,float,float,float,float,str)
    def setData(self, sp, pv, op, err, n, sts):
        self.dataSP.append(sp)
        self.dataPV.append(pv)
        self.dataOP.append(op)
        print(op)
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
        self.v1up.addItem(pg.PlotCurveItem(self.dataTime, self.dataSP, pen='#FFFFFF')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1up.addItem(pg.PlotCurveItem(self.dataTime, self.dataPV, pen='#FF007F'))
##        self.v2.addItem(pg.PlotCurveItem(self.dataTime, self.dataOP, pen='#FEFE2E'))
        self.v1upError.addItem(pg.PlotCurveItem(self.dataTime, self.dataError, pen='#FFFFFF'))
        self.v1upError.addItem(pg.PlotCurveItem(self.dataTime, self.errHor, pen='#00FF00'))

        if self.graphicState != True and len(self.dataTime) >= 11:
            if self.dataTime[-1] != self.span:
                self.v1up.setXRange(self.dataTime[-1] - self.span, self.dataTime[-1], padding = 0.3)
                self.v1up.setYRange(min(self.dataPV[-self.span:-1]), max(self.dataPV[-self.span:-1]), padding = 0.1)
##                self.v2.setYRange(min(-5,min(self.dataOP[-self.span:-1])), max(105, max(self.dataOP[-self.span:-1])), padding = 0.1)
                self.v1upError.setYRange(min(self.dataError[-self.span:-1]),max(self.dataError[-self.span:-1]), padding = 0.1)
                
    @Slot(float,float,float,float,float,str)
    def setDataTwo(self, sp, pv, op, err, n, sts):
        print("second thread", pv)
        self.dataSP_2.append(sp)
        self.dataPV_2.append(pv)
        self.dataOP_2.append(op)
        self.dataError_2.append(round(err,4))
        if err == 0:
            self.errHor_2.append(0)
        else:
            self.errHor_2.append(0)    
        self.dataTime_2.append(n)

        # |-* updater display
        self.updaterPV_2 = round(pv,6)
        self.updaterOP_2 = round(op,6)
        self.updaterState_2 = sts
        
        if self.updaterPV_2 == None:
            self.controller_2.PV.setText("BadValue")
            self.controller_2.OP.setText("BadValue")
        self.controller_2.PV.setText(str(self.updaterPV_2))
        if self.updaterState_2 == 'True' or self.updaterState_2 == 'Auto':
            self.controller_2.OP.setText(str(self.updaterOP_2))
        
        # |-* plot
        self.v1.addItem(pg.PlotCurveItem(self.dataTime_2, self.dataSP_2, pen='#FFFFFF')) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.v1.addItem(pg.PlotCurveItem(self.dataTime_2, self.dataPV_2, pen='#FF007F'))
##        self.v2up.addItem(pg.PlotCurveItem(self.dataTime_2, self.dataOP_2, pen='#FEFE2E'))
        self.v1Error.addItem(pg.PlotCurveItem(self.dataTime_2, self.dataError_2, pen='#FFFFFF'))
        self.v1Error.addItem(pg.PlotCurveItem(self.dataTime_2, self.errHor_2, pen='#00FF00'))

        if self.graphicState_2 != True and len(self.dataTime_2) >= 11:
            if self.dataTime_2[-1] != self.span_2:
                self.v1.setXRange(self.dataTime_2[-1] - self.span_2, self.dataTime_2[-1], padding = 0.3)
                self.v1.setYRange(min(self.dataPV_2[-self.span_2:-1]), max(self.dataPV_2[-self.span_2:-1]), padding = 0.1)
##                self.v2.setYRange(min(-5,min(self.dataOP[-self.span:-1])), max(105, max(self.dataOP[-self.span:-1])), padding = 0.1)
                self.v1Error.setYRange(min(self.dataError_2[-self.span_2:-1]),max(self.dataError_2[-self.span_2:-1]), padding = 0.1)

    def setParam(self, signal, obj):
        if obj.SP.text() !='' and obj.PV.text() !='' and obj.OP.text() !='':
            d = {"state": obj.modeButton.text(),"SP": float(obj.SP.text()),"PV": float(obj.PV.text()),"OP": float(obj.OP.text())} 
            signal.emit(d)
        

    def setConst(self, signal, obj):
        if obj.K1.text() !='' or obj.T1.text() !='' or obj.T2.text() !='':
            d = {"K1": float(obj.K1.text()), "T1": float(obj.T1.text()), "T2": float(obj.T2.text()),
                 "KLIN": float(obj.KLIN.text()), "KEXT": float(obj.KEXT.text()), "KNL": float(obj.KNL.text()),
                 "NLFM": float(obj.NLFM.text()), "NLGAIN": float(obj.NLGAIN.text()),"KGAP": float(obj.KGAP.text()),
                 "GAPLO": float(obj.GAPLO.text()), "GAPHI": float(obj.GAPHI.text())
                 }
            signal.emit(d) 

    def setModel(self, signal, obj):
        if obj.Kp.text() !='' and obj.Tp.text() !='' and obj.Dp.text() !='':
            d = {"Kp": np.float64(obj.Kp.text()), "Tp": np.float64(obj.Tp.text()), "Dp": np.float64(obj.Dp.text())}
            signal.emit(d)
        
            
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.graph.setWindowTitle('Variables(t)')
        self.graph.show()
        self.mainGL = pg.GraphicsLayout()
##        self.upper = pg.GraphicsLayout()
##        self.upperError = pg.GraphicsLayout()
##        self.lower = pg.GraphicsLayout()
##        self.lowerError = pg.GraphicsLayout()
##        self.mainGL.addLayout(self.upper, row=0, col = 2, rowspan =1, colspan = 3)
##        self.mainGL.addLayout(self.upperError, row=0, col = 6) #, rowspan =  1, colspan = 1)
##        self.mainGL.addLayout(self.lower, row=2, col = 2, rowspan  = 1, colspan = 3)
##        self.mainGL.addLayout(self.lowerError, row=2, col = 6) #, rowspan = 1, colspan = 1)

        self.upper = self.mainGL.addLayout(row=0, col = 2, rowspan =1, colspan = 3)
        self.emptyFiller = self.mainGL.addLayout(row=0, col=3)
        self.upperError = self.mainGL.addLayout(row=0, col = 6) #, rowspan =  1, colspan = 1)
        self.lower = self.mainGL.addLayout(row=2, col = 2, rowspan  = 1, colspan = 3)
        self.emptyFiller = self.mainGL.addLayout(row=2, col=3)
        self.lowerError = self.mainGL.addLayout(row=2, col = 6) #, rowspan = 1, colspan = 1)
        
        self.graph.setCentralWidget(self.mainGL)
        
        # v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
##        self.a2.setRange(-5,15)
        self.v2 = pg.ViewBox()
        self.lower.addItem(self.a2, row = 2, col = 2, rowspan = 2, colspan = 1)

        # cascade
        self.a2up = pg.AxisItem('left')
##        self.a2up.setRange(-5,15)
        self.v2up = pg.ViewBox()
        self.upper.addItem(self.a2up, row = 2, col = 2, rowspan = 2, colspan = 1)

        # v2 and a2 for error axis
##        self.a3 = pg.AxisItem('left')
##        self.a3.setRange(-5,15)
##        self.v3 = pg.ViewBox()
##        self.upperError.addItem(self.a3, row = 2, col = 1, rowspan = 2, colspan = 1)
        # cascade
##        self.a3up = pg.AxisItem('left')
##        self.a3up.setRange(-5,15)
##        self.v3up = pg.ViewBox()
##        self.lowerError.addItem(self.a3up, row = 2, col = 1, rowspan = 2, colspan = 1)
        
        # blank x-axis to alignment
##        ax = pg.AxisItem(orientation='bottom')
##        ax.setPen('#000000')
##        pos = (3,3)
##        self.lower.addItem(ax, *pos)
        
        # v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.lower.addItem(self.p1, row = 2, col = 3, rowspan = 2, colspan = 1)
        self.p1Error = pg.PlotItem()
        self.v1Error = self.p1Error.vb
        self.lowerError.addItem(self.p1Error, row = 0, col = 0) #, rowspan = 2, colspan = 1)
        # cascade
        self.p1up = pg.PlotItem()
        self.v1up = self.p1up.vb
        self.upper.addItem(self.p1up, row = 2, col = 3, rowspan = 2, colspan = 1)
        self.p1upError = pg.PlotItem()
        self.v1upError = self.p1upError.vb
        self.upperError.addItem(self.p1upError, row = 0, col = 0) #, rowspan = 2, colspan = 1)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})
        self.timeAxisError = pg.DateAxisItem(orientation='bottom')
        self.p1Error.setAxisItems({'bottom': self.timeAxisError})
        # cascade
        self.timeAxisUp = pg.DateAxisItem(orientation='bottom')
        self.p1up.setAxisItems({'bottom': self.timeAxisUp})
        self.timeAxisUpError = pg.DateAxisItem(orientation='bottom')
        self.p1upError.setAxisItems({'bottom': self.timeAxisUpError})

        # Mouse interaction
        self.upper.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        
        #grid
        self.p1.showGrid(x=True, y=True)
        
        self.p1up.showGrid(x=True, y=True)
        
        #Link between v1 and v2
        self.lower.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        
        self.upper.scene().addItem(self.v2up)
        self.a2up.linkToView(self.v2up)
        self.v2up.setXLink(self.v1up)
        
        #Link between v3 and v2 ad v1
##        self.lower.scene().addItem(self.v3)
##        self.a3.linkToView(self.v3)
##        self.v3.setXLink(self.v1)
        
##        self.upper.scene().addItem(self.v3up)
##        self.a3up.linkToView(self.v3up)
##        self.v3up.setXLink(self.v1up)
        
        #Axis label
        self.p1.getAxis('left').setLabel('SP vs PV',color='#FFFFFF')
        self.a2.setLabel('OP', color='#FEFE2E')
##        self.a3.setLabel('Error', color='#FEFE2E')
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1.sigResized.connect(self.updateViews)
        self.updateViews()

        self.p1Error.getAxis('left').setLabel('Error', color = '#00FF00')
        self.v1Error.enableAutoRange(axis=pg.ViewBox.XYAxes, enable = True)

        self.p1up.getAxis('left').setLabel('SP vs PV',color='#FFFFFF')
        self.a2up.setLabel('OP', color='#FEFE2E')
##        self.a3up.setLabel('Error', color='#FE2E2E')
        self.v1up.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v1up.sigResized.connect(self.updateViews)
        self.updateViews()

        self.p1upError.getAxis('left').setLabel('Error', color = '#00FF00')
        self.v1upError.enableAutoRange(axis=pg.ViewBox.XYAxes, enable = True)


        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())
        self.v2up.setGeometry(self.v1up.sceneBoundingRect())

        return
    
    def _on_mouse_clicked(self, event):
        self.graphicState = True
        self.graphicState_2 = True
        if event.double():
            self.graphicState = False
            self.graphicState_2 = False
        return self.graphicState, self.graphicState_2


class mainInput(QWidget):
    
    def __init__(self, title, parent = None):
        super().__init__(parent)
        self.title = title
        self.labelSP    = None
        self.labelPV    = None
        self.labelOP    = None
        self.modeButton = None
        self.casButton  = None
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

    def controlConfig(self, casButtonAdd = False):
        self.controlGroup = QGroupBox()
        self.controlGroup.setCheckable(True)
        self.controlGroup.setChecked(True)
        
        self.modeButton = QPushButton("Man")
        self.modeButton.setCheckable(True)

        self.casButton = QPushButton("Single")
        self.casButton.setCheckable(True)
        
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
        if casButtonAdd == True:
            layout.addWidget(self.casButton)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)

        return self.controlGroup


class controlComplex(QThread):
    signalBack_1 = Signal(float, float, float, float, float, str)
    PVConnectedFlag = Signal(bool)
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.state          = False
        self.cascade        = False
        self.DBActivated    = False
        self.SP             = 1
        self.PV             = 0
        self.OP             = 0
        self.PVlast         = None
        self.sample_time    = 1
        self.isRunning      = False
        self.n              = 0
        self.startTime      = 0
        self.deadTime       = 0
        self.bufferOP       = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
        self.K1             = 1.5
        self.T1             = 1
        self.T2             = 0.3
        self.KEXT           = 0
        self.KNL            = 0
        self.KLIN           = 0
        self.NLFM           = 0
        self.NLGAIN         = 0
        self.KGAP           = 0
        self.GAPLO          = 0
        self.GAPHI          = 0

        self.Kp             = 0.00437
        self.Tp             = 0.4
        self.uDesign        = 915.33
        self.PVDesign       = 22

        self.OPEUHI           = 100
        self.OPEULO           = 0
        self.PVEUHI         = 2.5
        self.PVEULO         = 0

        self.j              = 0
        self.didx           = 0
        self.dexpansion     = 0

        self.OPCas          = None
        self.uCas           = None
        self.uConnected     = False
        self.dbmodel        = self.Kp
        self.DB             = flakes.disturbance()
        
    def modeCall(self, instance):
        self.state = instance.isChecked()
        if instance.isChecked():
            instance.setText('Auto')
        else:
            instance.setText('Man')
        return self.state

    def casCall(self, instance):
        self.cascade = instance.isChecked()
        if instance.isChecked():
            instance.setText('Cascade')
        else:
            instance.setText('Single')
        return self.cascade
    
    # P and ID controller
    def run(self):
        self.isRunning = True
        pidOne = flakes.standard(self.sample_time)
        
        while self.isRunning:
            # signal updater  
            self.state = str(self.state)
            pidOne.name = 'rfopdt'

            if (self.cascade == True or self.cascade == 'Cascade' or self.cascade == 'True') and self.OPCas != None:
                self.SP = self.OPCas/100*(self.PVEUHI - self.PVEULO)
                
            self.SP = float(self.SP)
            self.PV = float(self.PV)
            self.OP = float(self.OP)
            
            self.Kp = float(self.Kp)
            self.Tp = float(self.Tp)
            self.deadTime = round(self.deadTime)

            if len(self.bufferOP) < self.deadTime + 1:
                for _ in range((self.deadTime+1) - len(self.bufferOP)):
                    self.bufferOP = np.insert(self.bufferOP,0,self.bufferOP[0])
            if len(self.bufferOP) > self.deadTime + 1:
                for _ in range(len(self.bufferOP) - (self.deadTime+1)):
                    self.bufferOP = np.delete(self.bufferOP,0)
                    
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
##            print()
##            print(self.SP)
##            print()
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
            pidOne.OP = self.OP

            # loop utility
            i = 0
            n = self.n
            self.startTime = time.time()
            while i < 1:
                if (self.state == 'True') or (self.state == 'Auto') or (self.state == True):
                    i += 1
                    n += 1
                    self.n = n
                    time.sleep(self.sample_time)
                    
                    # engineering units settings - system to controller
                    pidOne.PV[0] = pidOne.PV[0]/(self.PVEUHI - self.PVEULO)*100
                    pidOne.PV[1] = pidOne.PV[1]/(self.PVEUHI - self.PVEULO)*100
                    pidOne.SP = pidOne.SP/(self.PVEUHI-self.PVEULO)*100

#!()
##                    print()
##                    print("pidOne.PV", pidOne.PV)
##                    print("pidOne.SP", pidOne.SP)
##                    print()
#!()


                    # Gain modifier
                    if self.KLIN != 0:
                        if self.KGAP != 0 and (self.GAPLO != 0 or self.GAPHI != 0):
                            self.K1 = pidOne.narrowGain(pidOne.SP, pidOne.PV[1], self.KLIN, self.KGAP, self.GAPLO, self.GAPHI)

                        if self.NLFM != 0 and self.NLGAIN != 0:
                            self.K1 = pidOne.nonLinearGain(pidOne.error, self.KLIN, self.NLFM, self.NLGAIN) 

#!()
##                    print('After', self.K1)
##                    print()
#!()                    
                    
                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,self.K1,self.T1,self.T2) #pidOne.ioe = 0
                    PVlast = PVlast/100*(self.PVEUHI - self.PVEULO)
                    
                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
                    OP = self.bufferOP[0]

#!()
##                    print()
##                    print("OP controller IN",OP)
##                    print("PVlast controller IN", PVlast)
##                    print()
#!()

                    # engineering unit - controller to system
                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
                    u = u/100*self.uDesign
                    if self.uConnected == True and self.uCas != None:
                        u = self.uCas
                    y = (PVlast-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
                    y = y/100*self.PVDesign

#!()
##                    print()
##                    print("OP system IN",u)
##                    print("PV system IN",y)
##                    print()
#!()
                    #Disturbance model - noise constructor

                    if self.DBActivated == True:
                        self.j += 1
                        if (self.j - i) == self.dexpansion:
                            self.Kp = self.dbmodel[self.didx]
                            self.didx += 1
                            if self.didx == (len(self.dbmodel)-2):
                                self.didx = 0
                            self.j = 0
                        else:
                            self.Kp = self.Kp


                    # process model
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)

#!()
##                    print("PVnew system OUT",PVnew)
#!()
                    # engineering units settings - system to controller
                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
#!()
##                    print("PVnew controller OUT",PVnew)
#!()
                    self.OP = self.bufferOP[-1]
                    print()
                    print(self.OP)
                    print()
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
                    
                elif (self.state == 'False') or (self.state == 'Man') or (self.state == False):
                    i += 1
                    n += 1
                    self.n = n

                    # dead time shifter
                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
                    OP = self.bufferOP[0]
                    # dead time shifter-end
#!()
##                    print()
##                    print("OP controller IN",OP)
##                    print("PVlast controller IN", self.PV)
##                    print()
#!()

                    # engineering unit - controller to system
                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
                    u = u/100*self.uDesign
                    if self.uConnected == True and self.uCas != None:
                        u = self.uCas
                    y = (self.PV-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
                    y = y/100*self.PVDesign

#!()
##                    print()
##                    print("OP system IN",u)
##                    print("PV system IN",y)
##                    print()
#!()
                    # disturbance model - noise constructor
                    
                    if self.DBActivated == True:
                        self.j += 1
                        if (self.j - i) == self.dexpansion:
                            self.Kp = self.dbmodel[self.didx]
                            self.didx += 1
                            if self.didx == (len(self.dbmodel)-2):
                                self.didx = 0
                            self.j = 0
                        else:
                            self.Kp = self.Kp

                    
                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)

#!()
##                    print("PVnew system OUT",PVnew)
#!()
                    # engineering units settings - system to controller
                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
#!()
##                    print("PVnew controller OUT",PVnew)
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
        print()
        print(param)
        print()

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

    @Slot(float,float,float,float,float,str)
    def cascadeRecv(self, sp, pv, op, err, n, sts):
        self.OPCas  = op
        self.uCas   = pv

##class controlComplex2(QThread):
##    signalBack_2 = Signal(float, float, float, float, float, str)
##    
##    def __init__(self, parent = None):
##        super().__init__(parent)
##        self.state          = False
##        self.SP             = 1
##        self.PV             = 0
##        self.OP             = 0
##        self.PVlast         = None
##        self.sample_time    = 1
##        self.isRunning      = False
##        self.n              = 0
##        self.startTime      = 0
##        self.deadTime       = 0
##        self.bufferOP       = np.tile(float(self.OP), round(self.deadTime)+1) #must be in seconds
##        self.K1             = 1.5
##        self.T1             = 1
##        self.T2             = 0.3
##        self.KEXT           = 0
##        self.KNL            = 0
##        self.KLIN           = 0
##        self.NLFM           = 0
##        self.NLGAIN         = 0
##        self.KGAP           = 0
##        self.GAPLO          = 0
##        self.GAPHI          = 0
##
##        self.Kp             = 0.00437
##        self.Tp             = 0.4
##        self.uDesign        = 915.33
##        self.PVDesign       = 22
##
##        self.OPEUHI           = 100
##        self.OPEULO           = 0
##        self.PVEUHI         = 2.5
##        self.PVEULO         = 0
##
##        self.j              = 0
##        self.didx           = 0
##        self.dexpansion     = 0
##
##        
##    def modeCall(self, instance):
##        self.state = instance.isChecked()
##        if instance.isChecked():
##            instance.setText('Auto')
##        else:
##            instance.setText('Man')
##        return self.state
##    
##    # P and ID controller
##    def run(self):
##        self.isRunning = True
##        pidOne = flakes.standard(self.sample_time)
##        modelD = flakes.disturbance()
##        d, didl = modelD.modelDFile(r'C:\Users\ssv\Documents\MRM\Flakes\DmodelKp2.csv')
##        d = d
##        while self.isRunning:
##            # signal updater  
##            self.state = str(self.state)
##            pidOne.name = 'rfopdt'
##            self.SP = float(self.SP)
##            self.PV = float(self.PV)
##            self.OP = float(self.OP)
##            
##            self.Kp = float(self.Kp)
##            self.Tp = float(self.Tp)
##            self.deadTime = round(self.deadTime)
####            print('receiver',self.deadTime)
####            print('start', self.bufferOP)
##            if len(self.bufferOP) < self.deadTime + 1:
##                for _ in range((self.deadTime+1) - len(self.bufferOP)):
##                    self.bufferOP = np.insert(self.bufferOP,0,self.bufferOP[0])
####                    print('add', self.bufferOP)
##            if len(self.bufferOP) > self.deadTime + 1:
####                print("delta len",len(self.bufferOP) - (self.deadTime+1)) 
##                for _ in range(len(self.bufferOP) - (self.deadTime+1)):
##                    self.bufferOP = np.delete(self.bufferOP,0)
####                    print('less', self.bufferOP)
##                    
##            self.K1     = float(self.K1)
##            self.T1     = float(self.T1)
##            self.T2     = float(self.T2)
##            self.KLIN   = float(self.KLIN)
##            self.KEXT   = float(self.KEXT)
##            self.KNL    = float(self.KNL)
##            self.NLFM   = float(self.NLFM)
##            self.NLGAIN = float(self.NLGAIN)
##            self.KGAP   = float(self.KGAP)
##            self.GAPLO  = float(self.GAPLO)
##            self.GAPHI  = float(self.GAPHI)
##            
##            
###!()
##            print()
##            print(self.SP)
##            print()
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
###!()
##            # signal container
##            pidOne.SP = self.SP
##            pidOne.PV = [self.PVlast,self.PV]
####            print("first time", pidOne.PV)
##            pidOne.OP = self.OP
##
##            # loop utility
##            i = 0
##            n = self.n
##            self.startTime = time.time()
##            while i < 1:
##                if (self.state == 'True') or (self.state == 'Auto') or (self.state == True):
##                    i += 1
##                    n += 1
##                    self.n = n
##                    time.sleep(self.sample_time)
##                    
##                    # engineering units settings - system to controller
##                    pidOne.PV[0] = pidOne.PV[0]/(self.PVEUHI - self.PVEULO)*100
##                    pidOne.PV[1] = pidOne.PV[1]/(self.PVEUHI - self.PVEULO)*100
##                    pidOne.SP = pidOne.SP/(self.PVEUHI-self.PVEULO)*100
##
###!()
####                    print()
####                    print("pidOne.PV", pidOne.PV)
####                    print("pidOne.SP", pidOne.SP)
####                    print()
###!()
##
##
##                    # Gain modifier
##                    if self.KLIN != 0:
##                        if self.KGAP != 0 and (self.GAPLO != 0 or self.GAPHI != 0):
##                            self.K1 = pidOne.narrowGain(pidOne.SP, pidOne.PV[1], self.KLIN, self.KGAP, self.GAPLO, self.GAPHI)
##
##                        if self.NLFM != 0 and self.NLGAIN != 0:
##                            self.K1 = pidOne.nonLinearGain(pidOne.error, self.KLIN, self.NLFM, self.NLGAIN) 
##
###!()
####                    print('After', self.K1)
####                    print()
###!()                    
##                    
##                    OP, PVlast, pidOne.ioe = pidOne.pid(pidOne.SP, pidOne.OP, pidOne.ioe, pidOne.PV,self.K1,self.T1,self.T2) #pidOne.ioe = 0
##                    PVlast = PVlast/100*(self.PVEUHI - self.PVEULO)
##                    
##                    # dead time shifter
##                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, OP)
##                    OP = self.bufferOP[0]
##
###!()
####                    print()
####                    print("OP controller IN",OP)
####                    print("PVlast controller IN", PVlast)
####                    print()
###!()
##
##                    # engineering unit - controller to system
##                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
##                    u = u/100*self.uDesign
##                    y = (PVlast-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
##                    y = y/100*self.PVDesign
##
###!()
####                    print()
####                    print("OP system IN",u)
####                    print("PV system IN",y)
####                    print()
###!()
##                    #Disturbance model - noise constructor
##
##                    if True:
##                        self.j += 1
##                        if (self.j - i) == self.dexpansion:
##                            self.Kp = d[self.didx]
##                            self.didx += 1
##                            if self.didx == (len(d)-2):
##                                self.didx = 0
##                            self.j = 0
##                        else:
##                            self.Kp = self.Kp
##
##
##                    # process model
##                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)
##
###!()
####                    print("PVnew system OUT",PVnew)
###!()
##                    # engineering units settings - system to controller
##                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
##                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
###!()
####                    print("PVnew controller OUT",PVnew)
###!()
##                    self.OP = self.bufferOP[-1]
##                    self.PV = PVnew
##                    self.PVlast = PVlast
##                    self.state = self.state
##                    
##                    self.signalBack_2.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)
##
###!()
####                    print(self.SP)
####                    print(self.PV)
####                    print(self.PVlast)
####                    print(self.OP)
####                    print(self.state, end='\n\n')
###!()
##                    
##                elif (self.state == 'False') or (self.state == 'Man') or (self.state == False):
##                    i += 1
##                    n += 1
##                    self.n = n
##
##                    # dead time shifter
##                    self.bufferOP = pidOne.shiftBuffer(self.bufferOP, pidOne.OP)
##                    OP = self.bufferOP[0]
##                    # dead time shifter-end
###!()
####                    print()
####                    print("OP controller IN",OP)
####                    print("PVlast controller IN", self.PV)
####                    print()
###!()
##
##                    # engineering unit - controller to system
##                    u = (OP-self.OPEULO)*100/(self.OPEUHI-self.OPEULO)
##                    u = u/100*self.uDesign
##                    y = (self.PV-self.PVEULO)*100/(self.PVEUHI-self.PVEULO) #y is PVRaw = %
##                    y = y/100*self.PVDesign
##
###!()
####                    print()
####                    print("OP system IN",u)
####                    print("PV system IN",y)
####                    print()
###!()
##                    # disturbance model - noise constructor
##                    
##                    if True:
##                        self.j += 1
##                        if (self.j - i) == self.dexpansion:
##                            self.Kp = d[self.didx]
##                            self.didx += 1
##                            if self.didx == (len(d)-2):
##                                self.didx = 0
##                            self.j = 0
##                        else:
##                            self.Kp = self.Kp
##
##                    
##                    PVnew = pidOne.systemModel(pidOne._Flakes__model, y, u, self.Kp, self.Tp)
##
###!()
####                    print("PVnew system OUT",PVnew)
###!()
##                    # engineering units settings - system to controller
##                    PVnew = PVnew/self.PVDesign*100 #PVRaw = %
##                    PVnew = PVnew/100*(self.PVEUHI-self.PVEULO) + self.PVEULO
###!()
####                    print("PVnew controller OUT",PVnew)
###!()
##                    
##                    self.PVlast = self.PV
##                    self.PV = PVnew
##                    self.state = self.state
##                    
##                    self.signalBack_2.emit(self.SP, self.PV, self.OP, pidOne.error, self.startTime, self.state)
##                    time.sleep(self.sample_time)
##                    
##
##    def stop(self):
##        self.isRunning = False
##        self.quit()
##        self.terminate()
##    
##    @Slot(dict)
##    def dataReceiver(self, param):
##        self.state = param["state"]
##        self.SP = param["SP"]
##        self.PV = param["PV"]
##        self.OP = param["OP"]
##        print()
##        print(param)
##        print()
##
##    @Slot(dict)
##    def constReceiver(self, param):
##        self.K1         = param["K1"]
##        self.T1         = param["T1"]
##        self.T2         = param["T2"]
##        self.KLIN       = param["KLIN"]
##        self.KEXT       = param["KEXT"]
##        self.KNL        = param["KNL"]
##        self.NLFM       = param["NLFM"]
##        self.NLGAIN     = param["NLGAIN"]
##        self.KGAP       = param["KGAP"]
##        self.GAPLO      = param["GAPLO"]
##        self.GAPHI      = param["GAPHI"]
##
##    @Slot(dict)
##    def modelReceiver(self, param):
##        self.Kp             = param["Kp"]
##        self.Tp             = param["Tp"]
##        self.deadTime       = param["Dp"]

        
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
            

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = mainWindow()
        window.show()
        app.aboutToQuit.connect(window.complex_1.stop)
        app.aboutToQuit.connect(window.complex_2.stop)
        sys.exit(app.exec())
    except KeyboardInterrupt:
        window.complex_1.stop()
