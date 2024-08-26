from flakes import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename = r'C:\Users\ssv\Documents\MRM\Exp\UserLog.log',level = logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode = 'a')


        
class dataExt():
    fl  = flakes.disturbance()
    def __init__(self):
        self.n = 1
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

    def largeExt(self,path, gradeKey: list, *args, FileErrorFlag = False):
        
        for files in os.listdir(path):
            try:
                if '.' in files:
                    filePath = path + '\\' + files
                    self.df_init = pd.read_excel(filePath)
                    
                    for j in gradeKey:
                        idx = np.where(self.df_init == j)
                        if len(idx[0]) != 0:
                            break
                        
                    if len(idx[0]) != 0:
                        self.df = pd.read_excel(filePath, sheet_name = 1)
                        OP = self.dataBrowser(self.df, '202 B', opIdx = 1)
                        PV = self.dataBrowser(self.df, '202 B')
                        PPM = self.dataBrowser(self.df, '201-2', '201 - 2', '201 -2')

                        mydict = {'OP': OP, 'PV': PV, 'PPM': PPM}
                        self.dataPool(args[0] + '.xlsx', **mydict)
                        
                        logging.info(filePath + ':-> INDEX {}'.format(self.n))
                        self.n += 3
##                    self.dfGrade = pd.read_excel(filePath)
##                    grade = self.dataBrowser(self.dfGrade, 'GRADE PROD', searchObj = 'Grade')
##                    
##                    mydict = {'OP': grade, 'PV': grade, 'PPM': grade}
##                    self.dataPool(args[1] + '.xlsx', **mydict)
                    
                    
                elif '.' not in files:
                    print(self.n)
                    self.largeExt(path + '\\' + files, gradeKey,*args)
                else:
                    FileErrorFlag = True
            except:
                print('\n\n "WARNING FILE ERROR" \n {}\{} \n *-------------------* \n'.format(path, files))
                continue
            
    def dataBrowser(self, file: pd.DataFrame, *args, searchObj = 'FC', opIdx = 0):
        dataBlock = np.array([])
        for i in args:
            IdxKey = np.where(file == i)
            if len(IdxKey[0]) != 0:
                elemNum = len(IdxKey[0])
                if elemNum > 2:
                    print("WARNING: Three identical identifiers are FOUND !")
                FCrow = IdxKey[0][-1]
                FCcol = IdxKey[1][-1]
                if searchObj == 'FC':
                    for z in range(1,5):
                        dt = file.iloc[FCrow+z, FCcol+opIdx]
                        if isinstance(dt, str):
                            dt = -1
                        dataBlock = np.append(dataBlock,dt)
                    dataBlock = dataBlock[~np.isnan(dataBlock)]
                if searchObj == 'Grade':
                    for z in range(1,5):
                        dt = file.iloc[FCrow+z, FCcol+opIdx]
                        if dt == dt:
                            dataBlock = np.append(dataBlock,dt)
        
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
        

gradeKey2159 = ['MAS-2159', 'MAS 2159', 'MAS2159', 'MAS~2159']
gradeKey3355 = ['MAS-3355', 'MAS 3355', 'MAS3355', 'MAS~3355']
gradeKey3352 = ['MAS-3352', 'MAS 3352', 'MAS3352', 'MAS~3352']
gradeKey2345 = ['MAS-2345', 'MAS 2345', 'MAS2345', 'MAS~2345']

gradeKey = gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

print(gradeKey)

myd = dataExt()
myd.largeExt(r'D:\Polytama Propindo\Production - Documents\Bulk\Operations\2005\LST\LST~1', gradeKey, 'FC202A')

##npd = myd.excelExt(r"C:\Users\ssv\Documents\MRM\Exp\FC202A.xlsx")
##plots = myd.dataV(npd, 'FC202A')
