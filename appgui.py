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
# Plotting layout
import numpy as np
import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from PyQt6.QtWidgets import (QWidget,QApplication, QMainWindow,
                             QGridLayout, QLineEdit, QSpinBox,
                             QGroupBox, QDialog, QVBoxLayout,
                             QPushButton, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

class MW(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyApp")

        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(2,2)

        self.pg = pg.PlotWidget()

        bottomLayout = QHBoxLayout()
        space = QGroupBox("Space")
        bottomLayout.addWidget(space)

        layout.addWidget(self.pg,0,1,2,1)
        layout.addWidget(self.inputs(),0,0)
        layout.addWidget(self.inputs(),1,0)
        layout.addLayout(bottomLayout,3,3)
        
        
    def inputs(self):
        result = QGroupBox("Process Control")
        result.setCheckable(True)
        result.setChecked(True)
        modeButton = QPushButton("Auto")
        modeButton.setCheckable(True)
        labelSP = QLabel("SP")
        labelPV = QLabel("PV")
        labelOP = QLabel("OP")
        SP = QLineEdit()
        PV = QLineEdit()
        OP = QLineEdit()

        layout = QVBoxLayout(result)
        subLayout1 = QHBoxLayout()
        subLayout1.addWidget(labelSP)
        subLayout1.addWidget(SP)
        subLayout2 = QHBoxLayout()
        subLayout2.addWidget(labelPV)
        subLayout2.addWidget(PV)
        subLayout3 = QHBoxLayout()
        subLayout3.addWidget(labelOP)
        subLayout3.addWidget(OP)
        layout.addWidget(modeButton)
        layout.addLayout(subLayout1)
        layout.addLayout(subLayout2)
        layout.addLayout(subLayout3)
##        layout.addWidget(PV)
##        layout.addWidget(OP)
        return result
              
app = QApplication(sys.argv)
window = MW()
window.show()
app.exec()
        

