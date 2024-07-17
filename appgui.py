#====================================================================================#
# Layout allocation #

import sys

from PyQt5 import QtWidgets


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()

    label = QtWidgets.QLabel("Label")
    button = QtWidgets.QPushButton("Button")
    lineedit = QtWidgets.QLineEdit()

    left_gridlayout = QtWidgets.QGridLayout()
    right_gridlayout = QtWidgets.QGridLayout()

    left_widget = QtWidgets.QWidget()
    left_widget.setContentsMargins(0, 0, 0, 0)
    vbox = QtWidgets.QVBoxLayout(left_widget)
    vbox.setContentsMargins(0, 0, 0, 0)
    vbox.addWidget(label)

    button_and_lineedit_container = QtWidgets.QWidget()
    hlay_2 = QtWidgets.QHBoxLayout(button_and_lineedit_container)
    hlay_2.setContentsMargins(0, 0, 0, 0)
    hlay_2.addWidget(button)
    hlay_2.addWidget(lineedit, stretch=1)
    vbox.addWidget(button_and_lineedit_container)
    bottom_container = QtWidgets.QWidget()
    bottom_container.setContentsMargins(0, 0, 0, 0)
    bottom_container.setLayout(left_gridlayout)
    vbox.addWidget(bottom_container, stretch=1)

    right_widget = QtWidgets.QWidget()
    right_widget.setLayout(right_gridlayout)

    hlay = QtWidgets.QHBoxLayout(w)
    hlay.addWidget(left_widget, stretch=1)
    hlay.addWidget(right_widget, stretch=3)
  
    bottom_container.setStyleSheet("background-color:salmon;")
    right_widget.setStyleSheet("background-color:gray;")

    w.resize(640, 480)
    w.show()

    sys.exit(app.exec())

#================================================================================#

#!use/bin/env python
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

class mainWindow(QWidget):
    controlSignal_1 = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")

        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)
        controller_1 = mainInput('Process Control 1')
        setParam_1 = functools.partial(self.setParam, controlSignal_1)     
        controller_1.SP.returnPressed.connect(setParam_1)
        controller_1.PV.returnPressed.connect(setParam_1)
        controller_1.OP.returnPressed.connect(setPatam_1)
                                              
        controller_2 = mainInput('Process Control 2')
        signal_1 = mainInput('Signal 1')
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(controller_1.controlConfig(),0,0)
        layout.addWidget(controller_2.controlConfig(),1,0)
        layout.addLayout(signal_1.signalConfig(),4,1,2,1)

    def setParam(self, signal):
        if controller_1.SP.text() !='' and controller_1.PV.text() !='' and controller_1.OP.text() !='':
            d = {"SP": float(controller_1.SP.text()),"SP": float(controller_1.PV.text()),"SP": float(controller_1.OP.text())} 
            signal.emit(d)
            
    def graphConfig(self):
        self.graphWidget = pg.PlotWidget()
        
        return self.graphWidget

class mainInput():
    
    def __init__(self,title):
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
        signalBox = QGroupBox("Signal Configuration Box")
        signalBox.setCheckable(True)
        signalBox.setChecked(True)
        signalBox.setMinimumHeight(300)
        bottomLayout.addWidget(signalBox)
        
        return bottomLayout

    def controlConfig(self):
        result = QGroupBox("Process Control")
        result.setCheckable(True)
        result.setChecked(True)
        self.modeButton = QPushButton("Auto")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit()
        self.PV = QLineEdit()
        self.OP = QLineEdit()

        layout = QVBoxLayout(result)
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

        return result
              
app = QApplication(sys.argv)
window = mainWindow()
window.show()
sys.exit(app.exec())

#!use/bin/env python
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

class mainWindow(QWidget):
    controlSignal_1 = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Process Control Designer")

        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)
        
        controller_1 = mainInput('Process Control 1', self)
        controller_1.controlConfig()
        setParam_1 = functools.partial(self.setParam, self.controlSignal_1)     
        controller_1.SP.returnPressed.connect(setParam_1)
        controller_1.PV.returnPressed.connect(setParam_1)
        controller_1.OP.returnPressed.connect(setParam_1)

        controller_2 = mainInput('Process Control 2', self)
        controller_2.controlConfig()
                                              
        signal_1 = mainInput('Signal 1', self)
        layout.addWidget(self.graphConfig(),0,1,3,1)
        layout.addWidget(controller_1.controlConfig(),0,0)
        layout.addWidget(controller_2.controlConfig(),1,0)
        layout.addLayout(signal_1.signalConfig(),3,1,2,1)

    def setParam(self, signal):
        if controller_1.SP.text() !='' and controller_1.PV.text() !='' and controller_1.OP.text() !='':
            d = {"SP": float(controller_1.SP.text()),"SP": float(controller_1.PV.text()),"SP": float(controller_1.OP.text())} 
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
##        signalBox = QGroupBox("Signal Configuration Box")
##        signalBox.setCheckable(True)
##        signalBox.setChecked(True)
##        signalBox.setMinimumHeight(300)
##        bottomLayout.addWidget(signalBox)
        
        self.setCheckable(True)
        self.setChecked(True)
        self.setMinimumHeight(300)
        bottomLayout.addWidget(self)
        
        return bottomLayout

    def controlConfig(self):
##        result = QGroupBox("Process Control", self)
##        result.setCheckable(True)
##        result.setChecked(True)

##        self = QGroupBox("Process Control", self)
        self.setCheckable(True)
        self.setChecked(True)
        
        self.modeButton = QPushButton("Auto")
        self.modeButton.setCheckable(True)
        
        self.labelSP = QLabel("SP")
        self.labelPV = QLabel("PV")
        self.labelOP = QLabel("OP")
        self.SP = QLineEdit("0")
        self.PV = QLineEdit("0")
        self.OP = QLineEdit("0")

##        layout = QVBoxLayout(result)
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
              
app = QApplication(sys.argv)
window = mainWindow()
window.show()
sys.exit(app.exec())

