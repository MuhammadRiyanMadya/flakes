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
