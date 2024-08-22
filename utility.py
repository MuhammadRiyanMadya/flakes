from flakes import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd


class dataExt():
    fl  = flakes.disturbance()
    def __init__(self):
        pass
    def csvExt(self, path):
        y, _ = fl.modelDFile(path)
        fl.k = np.array([])
        x, _ = fl.modelDFile(path)
                                     
        mydict = dict(zip(FC202AKeys, FC202A))

        od = collections.OrderedDict(sorted(mydict.items()))
        del od[0]
        return y,x
    def excelExt(self, path, fromFolder = False):
        if fromFolder == False:
            df = pd.read_excel(path,header = 0)
            df = df.dropna(thresh =1).dropna(axis=1)
            df = df.sort_values(by=[df.columns.values[0]], ignore_index = True)
            npd = df.values

            return npd
        
    def dataV(self, npd):
        fig = plt.figure(1)
        num = npd.shape[1]
##        for i in range(1,num):
##            plt.plot(npd[:,0],npd[:,i])

        plt.plot(npd[:,0], npd[:,1])
        plt.show()

myD = dataExt()

npd = myD.excelExt(r"C:\Users\mrm\Downloads\MMR\Aptcon\Flakes\myData1.xlsx")
plots = myD.dataV(npd)

##from bokeh.models import Range1d, LinearAxis
##from bokeh.plotting import figure
##from bokeh.io import show
##
##fig = figure()
##
### Define x-axis
##fig.xaxis.axis_label = 'Date'
##
### Define 1st LHS y-axis
##fig.yaxis.axis_label = 'Pressure [barg]'
##fig.y_range = Range1d(start=0, end=200)
##
### Create 2nd LHS y-axis
##fig.extra_y_ranges['temp'] = Range1d(start=0, end=50)
##fig.add_layout(LinearAxis(y_range_name='temp', axis_label='Temperature [°C]'), 'left')
##
### Create 1st RHS y-axis
##fig.extra_y_ranges['lflow'] = Range1d(start=0, end=50000)
##fig.add_layout(LinearAxis(y_range_name='lflow', axis_label='Liquid Flowrate [bbl/day]'), 'right')
##
### Create 2nd RHS y-axis
##fig.extra_y_ranges['gflow'] = Range1d(start=0, end=50)
##fig.add_layout(LinearAxis(y_range_name='gflow', axis_label='Gas Flowrate [MMscf/day]'), 'right')
##
##fig.line(
##    x = [0,1,2,3,4,5],
##    y = [80,88,87,70,77,82],
##    legend_label = 'Pressure',
##    color = 'purple'
##)
##
##fig.line(
##    x = [0,1,2,3,4,5],
##    y = [5,6,5,5,5,4],
##    legend_label = 'Temperature',
##    y_range_name = 'temp',
##    color = 'red'
##)
##
##fig.line(
##    x = [0,1,2,3,4,5],
##    y = [10000,10100,10000,10150,9990,10000],
##    legend_label = 'Liquid Flowrate',
##    y_range_name = 'lflow',
##    color = 'orange'
##)
##
##
##fig.line(
##    x = [0,1,2,3,4,5],
##    y = [35,37,40,41,40,36],
##    legend_label = 'Gas Flowrate',
##    y_range_name = 'gflow',
##    color = 'green'
##)
##
##fig.toolbar_location = 'above'
##
##show(fig)
