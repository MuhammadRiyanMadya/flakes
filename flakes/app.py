####### Creating Simplest Window
##from PyQt6.QtCore import QSize, Qt
##from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
##import sys
##
##class MainWindow(QMainWindow):
##    def __init__(self):
##        super().__init__()
##        self.setWindowTitle("My App")
##        self.setMinimumSize(1200,1200)
##        button = QPushButton("Press Me!")
##        button.setCheckable(True)
##        button.clicked.connect(self.the_button_was_clicked)
##        self.setCentralWidget(button)
##        
##    def the_button_was_clicked(self, checked):
##        print("Clicked!", checked)
##
##    
##app = QApplication([])
##window = MainWindow()
##window.show()
##
##app.exec()

#!usr/bin/env python
# -*- coding: utf-8 -*-

##import pyqtgraph as pg
##from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow,
##                             QGridLayout, QLineEdit, QPushButton,
##                             QGroupBox, QVBoxLayout)
##import sys
##
##class MW(QWidget):
##    def __init__(self):
##        super().__init__()
##        self.setWindowTitle("AppSpec")
##
##        graphArea = pg.PlotWidget()
##        
##        controlNode = QGroupBox()
##        controlNode.setCheckable(True)
##        controlNode.setChecked(True)
##        modeButton = QPushButton()
##        SP = QLineEdit()
##        PV = QLineEdit()
##        OP = QLineEdit()
##
##        controlLayout = QVBoxLayout(controlNode)
##        controlLayout.addWidget(modeButton)
##        controlLayout.addWidget(SP)
##        controlLayout.addWidget(PV)
##        controlLayout.addWidget(OP)
##        
##        mainLayout = QGridLayout(self)
##        mainLayout.addLayout(controlLayout,0,0,1,1)
##        mainLayout.addWidget(graphArea,0,1,2,2)
##
##        
##app = QApplication(sys.argv)
##w = MW()
##w.show()
##app.exec()

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel,\
     QLineEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

import pyqtgraph as pg
import sys
import numpy as np
import time
        
class SignalContainer(QWidget):
    changeParam = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.title = 'Signal'
        self.span = 10
        self.time = []
        self.data = []
        self.initUI()

    @Slot(float, float)
    def setData(self, t, d):
        self.time.append(t)
        self.data.append(d)
##        self.time.pop(0)
##        self.data.pop(0)
##        self.graphWidget.clear()
        self.graphWidget.plot(self.time, self.data) #, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
##        if self.time[-1] != self.span:
##            self.graphWidget.setXRange(self.time[-1] - self.span, self.time[-1], padding = 0)
##        self.graphWidget.setYRange(min(-2, min(self.data)), max(2, max(self.data)), padding = 0.1)
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(800,800)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.ampLabel = QLabel("Amp")
        self.amp = QLineEdit("2")
        self.amp.returnPressed.connect(self.setParam)

        self.freqLabel = QLabel("Freq")
        self.freq = QLineEdit("1")
        self.freq.returnPressed.connect(self.setParam)

        self.sampLabel = QLabel("Ts")
        self.samp = QLineEdit("0.02")
        self.samp.returnPressed.connect(self.setParam)

        self.conf = QPushButton("Configure")
        self.conf.clicked.connect(self.setParam)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.ampLabel)
        buttonLayout.addWidget(self.amp)
        buttonLayout.addWidget(self.freqLabel)
        buttonLayout.addWidget(self.freq)
        buttonLayout.addWidget(self.sampLabel)
        buttonLayout.addWidget(self.samp)
        buttonLayout.addWidget(self.conf)
        layout.addLayout(buttonLayout)

        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        self.pen = pg.mkPen(color=(255,0,0), width = 3)
        self.graphWidget.setBackground((50,50,50,220))
        self.graphWidget.setTitle("Signal(t)", color='w',size='20pt')
        styles={'color':'r', 'font-size':'20px'}
        self.graphWidget.setLabel('left','signal [SI]',**styles)
        self.graphWidget.setLabel('bottom', 'time [s]', **styles)
        self.graphWidget.showGrid(x = True, y = True)
        self.graphWidget.addLegend()
        self.graphWidget.setXRange(0, self.span, padding = 0)
        self.graphWidget.setYRange(-2,2, padding = 0.1)
        self.graphWidget.plot(self.time, self.data, name="signal", pen = self.pen, symbol = '+', symbolSize = 5, symbolBrush = 'w')
        self.th = Thread(self)
        self.amp.setText(str(self.th.amp))
        self.freq.setText(str(self.th.freq))
        self.samp.setText(str(self.th.samp))
        self.th.changeData.connect(self.setData)
        self.changeParam.connect(self.th.setParam)
        self.th.start()

    def setParam(self):
        if self.amp.text() !='' and self.freq.text() !='' and self.samp.text() !='':
            if float(self.samp.text()) != 0:
                d = {"amp":float(self.amp.text()), "freq":float(self.freq.text()), "samp":float(self.samp.text())}
                self.changeParam.emit(d)

class Thread(QThread):
    changeData = Signal(float,float)

    def __init__(self, a):
        super().__init__()
        self.amp = 2
        self.freq = 1
        self.samp = 0.02
        self.time = 0
        self.data = 0
    
    def run(self):
        self.isRunning = True
        while self.isRunning:
            self.time += self.samp
            self.data = self.amp*np.sin(2*np.pi*self.freq*self.time)
            self.changeData.emit(self.time, self.data)
            time.sleep(2)

    def stop(self):
        self.isRunning = False
        self.quit()
        self.terminate()

    @Slot(dict)
    def setParam(self, param):
        self.amp = param["amp"]
        self.freq = param["freq"]
        self.samp = max(0.0001, param["samp"])
                        
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalContainer()
    window.show()
    app.aboutToQuit.connect(window.th.stop)
    sys.exit(app.exec())


####### Signals and slots

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
from random import choice

window_titles = [
    'My App',
    'My App',
    'Still My App',
    'Still My App',
    'What on earth',
    'What on earth',
    'This is surprising',
    'This is surprising',
    'Something when wrong'
    ]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.n_times_clicked = 0

        self.setWindowTitle("My App")

        self.button = QPushButton("Press Me!")
        self.button.clicked.connect(self.the_button_was_clicked)

        self.windowTitleChanged.connect(self.the_window_title_changed)

        self.setCentralWidget(self.button)

    def the_button_was_clicked(self):
        print("Clicked.")
        new_window_title = choice(window_titles)
        print(Setting title
import sys
import random
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        ## Creating the Widgets and Layouts
        self.plot_widget = pg.PlotWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.sbutton = QtWidgets.QPushButton("Start / Continue")
        self.ebutton = QtWidgets.QPushButton("Stop")
        self.timer = pg.QtCore.QTimer()
        self.scroll = QtWidgets.QSlider()
        ## Creating the variables and constants
        self.data = [[0], [random.randint(0,9)]]  ## [xVal, yVal] to create less variables
        self.plot_item = self.plot_widget.plot(*self.data)
        self.plot_widget.setYRange(0, 10)
        self.xTime = self.genTime()
        self.vsize = 10
        self.psize = 30
        ## Building the Widget
        self.setLayout(self.layout)
        self.layout.addWidget(self.sbutton)
        self.layout.addWidget(self.ebutton)
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.scroll)
        ## Changing some properties of the widgets
        self.plot_widget.setMouseEnabled()
        self.ebutton.setEnabled(False)
        self.scroll.setEnabled(True)
        self.scroll.setMaximum(self.psize-self.vsize)
        self.scroll.setValue(self.psize-self.vsize)
        ## Coneccting the signals
        self.sbutton.clicked.connect(self.start)
        self.ebutton.clicked.connect(self.stop)
        self.timer.timeout.connect(self.update)
        self.scroll.valueChanged.connect(self.upd_scroll)

    def genTime(self):  # used to generate time
        t = 0
        while True:
            t += np.random.random_sample()
            yield t
            t = np.ceil(t)

    def upd_scroll(self):
        val = self.scroll.value()
        xmax = np.ceil(self.data[0][-1+self.vsize-self.psize+val])-1
        xmin = xmax-self.vsize
        self.plot_widget.setXRange(xmin, xmax)

    def update(self):
        num = len(self.data[0])
        if num <= self.psize:
            self.plot_item.setData(*self.data)
        else:
            self.plot_item.setData(
                self.data[0][-self.psize:],
                self.data[1][-self.psize:]
            )

        if num == self.vsize:
            self.scroll.setEnabled(True)
        self.data[0].append(next(self.xTime))
        self.data[1].append(random.randint(0,9))
        if num > self.vsize :
            self.upd_scroll()
     
    def start(self):
        self.sbutton.setEnabled(False)
        self.ebutton.setEnabled(True)
        self.timer.start(1000)

    def stop(self):
        self.sbutton.setEnabled(True)
        self.ebutton.setEnabled(False)
        self.timer.stop()
        self.upd_scroll()
        
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
from PySide6 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os
from random import randint

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))
        self.y = [randint(0,100) for _ in range(100)]
        self.graphWidget.setBackground('k')
        
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
