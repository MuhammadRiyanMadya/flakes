import pandas as pd
import numpy as np

from PySide6.QtWidgets import (QWidget,QApplication, QMainWindow,
                               QGridLayout, QLineEdit, QSpinBox,
                               QGroupBox, QDialog, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout,
                               QSpinBox, QTabWidget, QSizePolicy,
                               QTableWidget)
import pyqtgraph as pg
from pyqtgraph import QtCore
import sys
import time

import os
from datetime import datetime

import time

timestamp1 = time.mktime(time.strptime('2024-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
timestamp2 = time.mktime(time.strptime('2024-08-01 00:00:00', '%Y-%m-%d %H:%M:%S'))

date = []
while timestamp1 < timestamp2:
    date.append(timestamp1)
    timestamp1 = timestamp1+3600
print()
print(datetime.fromtimestamp(date[-1]).strftime('%Y-%m-%d %H:%M:%S'))

def xyleneOpener(path):
    tdDB = np.array([])
    xylDB = np.array([])
    counter = 1
    for docs in os.listdir(path):
        newpath = os.chdir(path + '\\' + docs)
            
        for file in os.listdir(newpath):
            if '.xlsx' in file or '.XLSx':

                df = pd.read_excel(file, header = 0, usecols="B:O")

                xylBool = df == 'XYL'
                if len(np.nonzero(xylBool.values)[1]) == 0:
                    xylBool = df == 'xyl'
                xylindex = np.nonzero(xylBool.values)[1][0]

                tdBool = df == 'T/D Ratio'
                if len(np.nonzero(tdBool.values)[1]) == 0:
                    tdBool = df == 'T/D ratio'
                tdindex = np.nonzero(tdBool.values)[1][0]

                df = df.values
                tdDB = np.append(tdDB, df[:,tdindex][15:39])
                xylDB = np.append(xylDB, df[:,xylindex][15:39])

                counter += 1
    numberDB = np.linspace(1,len(tdDB),len(tdDB))
    
    for val in xylDB:
        if type(val) == str:
            valindex = np.where(xylDB == val)
            xylDB[valindex[0][0]] = np.nan

    for val in tdDB:
        if type(val) == str:
            valindex = np.where(tdDB == val)
            tdDB[valindex[0][0]] = np.nan
            
                
    return numberDB, tdDB, xylDB

def dataNormalizer(data):    
    i = 0
    index = 0
    while i < len(data):
        if not np.isnan(data[i]):
            index = i
        else:
            data[i] = data[index]
        i += 1
    return data


df = pd.read_csv(r'C:\Users\ssv\Documents\MRM\PP\xyleneDB.csv', header = None)
numDB = df.values.T[0]
tdrDB = df.values.T[1]
xylDB = df.values.T[2]

tdrDB = dataNormalizer(tdrDB)
xylDB = dataNormalizer(xylDB)
tdr = list(tdrDB)
xyl = list(xylDB)

xylHigh = []
xylLow = []
for i in numDB:
    xylHigh.append(5)
    xylLow.append(2.5)

class mainWindow(QWidget):
    
    def __init__(self, xdata, ydata1, ydata2):
        super().__init__()
        self.setWindowTitle("History Peaks")
        layout = QGridLayout(self)
        layout.setContentsMargins(10,10,10,10)

        self.xdata = xdata
        self.ydata1 = ydata1
        self.ydata2 = ydata2

        layout.addWidget(self.graphConfig())
    def setItem(self, pos):
        pos = time.mktime(time.strptime(pos, '%Y-%m-%d %H:%M:%S'))
        self.v1.addItem(pg.InfiniteLine(pos, angle=90, movable = False,name='HR -> ZN', pen=pg.mkPen('g', width=1, style=QtCore.Qt.SolidLine)))
        
    def graphConfig(self):
        self.graph = pg.GraphicsView()
        self.graph.setWindowTitle('History Peaks')
        self.graph.show()
        self.l = pg.GraphicsLayout()
        self.graph.setCentralWidget(self.l)
        
        #v2 and a2 for additional graph and y axis
        self.a2 = pg.AxisItem('left')
        self.v2 = pg.ViewBox()
        self.l.addItem(self.a2, row = 2, col = 0, rowspan = 1, colspan = 1)
        
        # blank x-axis to alignment
##        ax = pg.AxisItem(orientation='bottom')
##        ax.setPen('#000000')
##        pos = (2,0)
##        self.l.addItem(ax, *pos)
        
        #v1 is the main plot, it has its own box
        self.p1 = pg.PlotItem()
        self.v1 = self.p1.vb
        self.l.addItem(self.p1, row = 2, col = 2, rowspan = 1, colspan = 2)
        self.p1LeftAxis = self.p1.getAxis('left')
        pos = (2,4)
        self.l.addItem(self.p1LeftAxis, *pos)

        # time axis
        self.timeAxis = pg.DateAxisItem(orientation='bottom')
        self.p1.setAxisItems({'bottom': self.timeAxis})

        
        #grid
        self.p1.showGrid(x=True, y=True)
        #Link between v1 and v2
        self.l.scene().addItem(self.v2)
        self.a2.linkToView(self.v2)
        self.v2.setXLink(self.v1)
        #Axis label
        self.p1.getAxis('left').setLabel('TD ratio', color='#2E2EFE')
        self.p1.getAxis('bottom').setLabel('Time', color='#000000')
        self.a2.setLabel('Xylene %', color='#FEFE2E')

        self.v1.addItem(pg.PlotCurveItem(self.xdata, self.ydata1, pen='#2E2EFE'))
        self.v2.addItem(pg.PlotCurveItem(self.xdata, self.ydata2, pen='#FEFE2E'))
        self.v2.addItem(pg.PlotCurveItem(self.xdata, xylHigh, pen='#FEFE2E'))
        self.v2.addItem(pg.PlotCurveItem(self.xdata, xylLow, pen='#FEFE2E'))

        self.v1.sigResized.connect(self.updateViews)
        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v2.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=False)
        self.updateViews()

  

        self.v1.setXRange(min(self.xdata), max(self.xdata))
        self.v1.setYRange(0,400, padding = 0.1)
        self.v2.setYRange(0,6, padding = 0.1)
        region = pg.LinearRegionItem()
        region.setZValue(1000)
        self.v1.addItem(region, ignoreBounds = True)
        

        return self.graph
    
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())

        return

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow(date, tdr, xyl)
    window.setItem('2024-07-26 00:00:00')
    window.show()
    sys.exit(app.exec())

import pandas as pd
import numpy as np
import os
import sys


##def xyleneOpener(path):
##    tdDB = np.array([])
##    xylDB = np.array([])
##    counter = 1
##    for docs in os.listdir(path):
##        newpath = os.chdir(path + '\\' + docs)
##            
##        for file in os.listdir(newpath):
##            if '.xlsx' in file or '.XLSx':
##
##                df = pd.read_excel(file, header = 0, usecols="B:O")
##
##                xylBool = df == 'XYL'
##                if len(np.nonzero(xylBool.values)[1]) == 0:
##                    xylBool = df == 'xyl'
##                xylindex = np.nonzero(xylBool.values)[1][0]
##
##                tdBool = df == 'T/D Ratio'
##                if len(np.nonzero(tdBool.values)[1]) == 0:
##                    tdBool = df == 'T/D ratio'
##                tdindex = np.nonzero(tdBool.values)[1][0]
##
##                df = df.values
##                tdDB = np.append(tdDB, df[:,tdindex][15:39])
##                xylDB = np.append(xylDB, df[:,xylindex][15:39])
##
##                counter += 1
##    numberDB = np.linspace(1,len(tdDB),len(tdDB))
##    
##    for val in xylDB:
##        if type(val) == str:
##            valindex = np.where(xylDB == val)
##            xylDB[valindex[0][0]] = np.nan
##
##    for val in tdDB:
##        if type(val) == str:
##            valindex = np.where(tdDB == val)
##            tdDB[valindex[0][0]] = np.nan
##            
##                
##    return numberDB, tdDB, xylDB
##
##def dataNormalizer(data):    
##    i = 0
##    index = 0
##    while i < len(data):
##        if not np.isnan(data[i]):
##            index = i
##        else:
##            data[i] = data[index]
##        i += 1
##    return data


##time = np.linspace(1,100,100)
##data1 = np.linspace(200,2300,99)
##data1 = np.append(data1, None)
##datadf = pd.DataFrame(np.vstack((time, data1)).T, columns = ['time', 'data1'])
##datadf.rename(columns={'time':'Time'}, inplace = True)
##
##filename = 'DataExperiment.xlsx'
##
##with pd.ExcelWriter(filename) as writer:
##    datadf.to_excel(writer, header = None, index = False)
##
##dfImport = pd.read_excel('DataExperiment.xlsx')
##lastrow = len(dfImport.iloc[:,0])
##print(lastrow)
##
##data1 = np.linspace(200,2300,99)
##data1 = np.append(data1, None)
##datadf = pd.DataFrame(np.vstack((time, data1)).T, columns = ['time', 'data1'])
##
##
##with pd.ExcelWriter('DataExperiment.xlsx',
##                    mode = 'a',
##                    if_sheet_exists ='overlay'
##                    ) as writer:
##    datadf.to_excel(writer, header = None, startrow = lastrow+1, index = False)
##
##dfImport = pd.read_excel('DataExperiment.xlsx')
##print(dfImport.values)

def reader(path, ext):
    
    fileBuffer = [file for file in os.listdir(path) if '.' in file]
    folderBuffer = [file for file in os.listdir(path) if '.' not in file]

##    for file in os.listdir(path):
##        print(file)
##        if ext in file:
##            df = pd.read_excel(path + '\\' + file)
##            print(df)
##        elif '.' not in file:
##            reader(path + '\\' + file, ext)
    return fileBuffer, folderBuffer
             
            
fileList, folderList = reader(r'C:\Users\ssv\Documents\MRM\PP\Catalyst', '.xlsx')


"""
This example shows how to insert text into a scene using TextItem. This class 
is for displaying text that is anchored to a particular location in the data
coordinate system, but which is always displayed unscaled. 

For text that scales with the data, use QTextItem. 
For text that can be placed in a layout, use LabelItem.
"""

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

x = np.linspace(-20, 20, 1000)
y = np.sin(x) / x
plot = pg.plot()   ## create an empty plot widget
plot.setYRange(-1, 2)
plot.setWindowTitle('pyqtgraph example: text')
curve = plot.plot(x,y)  ## add a single curve

## Create text object, use HTML tags to specify color/size
text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>', anchor=(-0.3,0.5), angle=45, border='w', fill=(0, 0, 255, 100))
plot.addItem(text)
text.setPos(0, y.max())

## Draw an arrowhead next to the text box
arrow = pg.ArrowItem(pos=(0, y.max()), angle=-45)
plot.addItem(arrow)


## Set up an animated arrow and text that track the curve
curvePoint = pg.CurvePoint(curve)
plot.addItem(curvePoint)
text2 = pg.TextItem("test", anchor=(0.5, -1.0))
text2.setParentItem(curvePoint)
arrow2 = pg.ArrowItem(angle=90)
arrow2.setParentItem(curvePoint)

## update position every 10ms
index = 0
def update():
    global curvePoint, index
    index = (index + 1) % len(x)
    curvePoint.setPos(float(index)/(len(x)-1))
    text2.setText('[%0.1f, %0.1f]' % (x[index], y[index]))
    
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)

if __name__ == '__main__':
    pg.exec()
