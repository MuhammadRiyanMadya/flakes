from flakes import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


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
        
    def dataV(self, npd, valveLabel: str):
##        fig = plt.figure(1)
##        num = npd.shape[1]
####        for i in range(1,num):
####            plt.plot(npd[:,0],npd[:,i])
##
##        plt.plot(npd[:,0], npd[:,1])
##        plt.show()

        fig, ax1 = plt.subplots()

        ax1.plot(npd[:,0], npd[:,1], linestyle = 'dashed',linewidth = 0.5, color = 'blue', label = valveLabel, marker = '.', markerfacecolor ='yellow', markersize = 7)
        ax1.set_xlabel('OP, %')
        ax1.set_ylabel('H2 kg/h', color = 'b')
        ax1.tick_params('y', colors='b')
        ax1.xaxis.set_major_locator(MultipleLocator(1))
##        ax1.yaxis.set_major_locator(MultipleLocator(0.025))

        ax2 = ax1.twinx()

        ax2.plot(npd[:,0], npd[:,2], label = 'PPM', linewidth = 0.5,color = 'red', linestyle ='dashed', marker ='.', markerfacecolor =  'yellow', markersize = 7)
        ax2.set_ylabel('PPM', color='r')
        ax2.tick_params('y', colors = 'r')

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        lines = lines1 + lines2
        labels = labels1 + labels2

        plt.legend(lines, labels, loc = 'upper right')

        plt.title(f'{valveLabel} Valve Trend', fontsize = 16, fontweight = 'bold')
        plt.show()

    def largeExt(self,path, fromFolder = False):
        if fromFolder == False:
            self.df = pd.read_excel(path, sheet_name = 1)

            FC201B_PV = self.dataBrowser(self.df, '201 B')
            FC201B_OP = self.dataBrowser(self.df, '201 B', opIdx = 1)
            AC201_1 = self.dataBrowser(self.df, '201-1', '201 - 1', '201 -1')

            mydict = {'OP': FC201B_OP, 'PV': FC201B_PV, 'PPM': AC201_1}

            self.dataPool('dataExperiment.xlsx', **mydict)
            

    def dataBrowser(self, file: pd.DataFrame, *args, opIdx = 0):
        dataBlock = np.array([])
        for i in args:
            IdxKey = np.where(file == i)
            if len(IdxKey[0]) != 0:
                elemNum = len(IdxKey[0])
                if elemNum > 2:
                    print("WARNING: Three identical identifiers are FOUND !")
                FCrow = IdxKey[0][-1]
                FCcol = IdxKey[1][-1]
                for i in range(1,5):
                    dt = file.iloc[FCrow+i, FCcol+opIdx]
                    if isinstance(dt, str):
                        dt = -1
                    dataBlock = np.append(dataBlock,dt)
        dataBlock = dataBlock[~np.isnan(dataBlock)]
##            if len(dataBlock) == 3)

        return dataBlock

    def dataPool (self, filename, **kwargs):
        data_1 = kwargs['OP']
        data_2 = kwargs['PV']
        data_3 = kwargs['PPM']
        datadf_input = pd.DataFrame(np.vstack((data_1, data_2, data_3)).T, columns = list(kwargs.keys()))

        try:
            datadf_excel = pd.read_excel(filename)
            lastrow = len(datadf_excel.iloc[:,0])
        except Exception as e:
            with pd.ExcelWriter(filename) as writer:
                datadf_input.to_excel(writer, header = None, index = False)
            datadf_excel = pd.read_excel(filename)
            lastrow = len(datadf_excel.iloc[:,0])

        with pd.ExcelWriter(filename,
                            mode = 'a',
                            if_sheet_exists = 'overlay'
                            ) as writer:
            datadf_input.to_excel(writer, header = None, index = False, startrow = lastrow + 1)

        
            
        
        
myd = dataExt()
myd.largeExt(r'C:\Users\mrm\Downloads\MMR\Aptcon\Flakes\largeData Extraction Lab\LST_1\LST~1\01~JAN\03.XLS')



##myD = dataExt()
##
##npd = myD.excelExt(r"C:\Users\mrm\Downloads\MMR\Aptcon\Flakes\FC202A.xlsx")
##plots = myD.dataV(npd, 'FC202A')

