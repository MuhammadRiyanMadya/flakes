import sys
sys.path.append('../flakes')
import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename = r'C:\Users\ssv\Documents\MRM\Exp\LargeDataExtractor\UserLogValve_2019.log',level = logging.INFO,
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
            df = pd.read_excel(path)
            df = df.dropna(thresh =1).dropna(axis=1)
            df = df.sort_values(by=[df.columns.values[0]], ignore_index = True)
            print(df)
            df = df[df.iloc[:,2] < 600]
            print(df)
            npd = df.values

            return npd
        
    def dataV(self, npd, valveLabel: str):

        fig, ax1 = plt.subplots()

        ax1.plot(npd[:,0], npd[:,1], linestyle = 'dashed',linewidth = 0.5, color = 'blue', label = valveLabel, marker = '.', markerfacecolor ='yellow', markersize = 7)
        ax1.set_xlabel('OP, %')
        ax1.set_ylabel('H2 kg/h', color = 'b')
        ax1.tick_params('y', colors='b')
        ax1.xaxis.set_major_locator(MultipleLocator(2))
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

    def largeExt(self,path, gradeKey: list, *args,FileErrorFlag = False):
        
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

##                        OP = self.dataBrowser(self.df, 'A      B', opIdx = 1)
##                        PV = self.dataBrowser(self.df, 'A      B')
                        OP = self.dataBrowser(self.df, '201 B', opIdx = 1)
                        PV = self.dataBrowser(self.df, '201 B')
                        PPM = self.dataBrowser(self.df, '201-1', '201 - 1', '201 -1')

                        mydict = {'OP': OP, 'PV': PV, 'PPM': PPM}
                        self.dataPool(args[0] + '.xlsx', **mydict)
                        
                        logging.info(filePath + ':-> INDEX {}'.format(self.n))
                        self.n += 3
                        
##                    self.dfGrade = pd.read_excel(filePath)
##                    grade = self.dataBrowser(self.dfGrade, 'GRADE PROD', searchObj = 'Grade')
##                    
##                    mydict = {'OP': grade, 'PV': grade, 'PPM': grade}
##                    self.dataPool(args[0] + '.xlsx', **mydict)
##
##                    logging.info(filePath + ':-> INDEX {}'.format(self.n))
##                    self.n += 3
                    
                    
                elif '.' not in files:
                    print(self.n)
                    self.largeExt(path + '\\' + files, gradeKey, *args)
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
                # General
                FCrow = IdxKey[0][-1]
                FCcol = IdxKey[1][-1]
                # 201 2023,2024
##                FCrow = IdxKey[0][0]
##                FCcol = IdxKey[1][0]
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

gradeKey2161 = ['MAS 2161']
gradeKey2161 = ['MAS 2162']
gradeKey2158 = ['MAS-2158', 'MAS 2158', 'MAS2158', 'MAS - 2158']
gradeKey2159 = ['MAS-2159', 'MAS 2159', 'MAS2159', 'MAS~2159']
gradeKey3355 = ['MAS-3355', 'MAS 3355', 'MAS3355', 'MAS~3355']
gradeKey3352 = ['MAS-3352', 'MAS 3352', 'MAS3352', 'MAS~3352']
gradeKey2345 = ['MAS-2345', 'MAS 2345', 'MAS2345', 'MAS~2345']

gradeKey = gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

gradeKey_2008 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2010 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2012 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2014 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2016 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2018 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2019 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2020 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2021 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2022 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2023 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
gradeKey_2024 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

myd = dataExt()
##myd.largeExt(r'D:\Polytama Propindo\Production - Documents\Bulk\Operations\2019\LST-2019\LST~1',gradeKey_2019,'FC201A_2019')

npd = myd.excelExt(r"./FC201A_2024.xlsx")
plots = myd.dataV(npd, 'FC201A_2024')

import sys
sys.path.append('../flakes')
import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename = r'C:\Users\ssv\Documents\MRM\Exp\LargeDataExtractor\UserLogValve_2019.log',level = logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode = 'a')

        
class dataExt():
    
    fl  = flakes.disturbance()
    
    def __init__(self, fileName):
        self.n = 1
        self.name = fileName
        self.excelSaveLoc = os.getcwd()
        
    def csvExt(self, path):
        y, _ = fl.modelDFile(path)
        fl.k = np.array([])
        x, _ = fl.modelDFile(path)
                                     
        mydict = dict(zip(FC202AKeys, FC202A))

        od = collections.OrderedDict(sorted(mydict.items()))
        del od[0]
        return y,x
    
    def excelExt(self, columnLimit=2, limit=600, fromFolder = False):
        """
        Default structure:
        column 1: valve opening
        column 2: flow value
        column 3: ppm hydrogen
        column n: additional parameters
        """
        path = self.excelSaveLoc + '/' + self.name + '.xlsx'
        if fromFolder == False:
            df = pd.read_excel(path)
            df = df.dropna(thresh =1).dropna(axis=1)
            df = df.sort_values(by=[df.columns.values[0]], ignore_index = True)
            df = df[df.iloc[:,columnLimit] < limit]
            npdata = df.values

            return npdata
        
    def dataV(self, npdata, secondData= True):

        fig, ax1 = plt.subplots()

        ax1.plot(npd[:,0], npd[:,1], linestyle = 'dashed',linewidth = 0.5, color = 'blue', label = self.name, marker = '.', markerfacecolor ='yellow', markersize = 7)
        ax1.set_xlabel('OP, %')
        ax1.set_ylabel('H2 kg/h', color = 'b')
        ax1.tick_params('y', colors='b')
        ax1.xaxis.set_major_locator(MultipleLocator(2))
##        ax1.yaxis.set_major_locator(MultipleLocator(0.025))

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines = lines1
        labels = labels1
        if secondData == True:
            ax2 = ax1.twinx()
            ax2.plot(npd[:,0], npd[:,2], label = 'PPM', linewidth = 0.5,color = 'red', linestyle ='dashed', marker ='.', markerfacecolor =  'yellow', markersize = 7)
            ax2.set_ylabel('PPM', color='r')
            ax2.tick_params('y', colors = 'r')
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines = lines1 + lines2
            labels = labels1 + labels2

        plt.legend(lines, labels, loc = 'upper right')
        plt.title(f'{self.name} Valve Trend', fontsize = 16, fontweight = 'bold')
        plt.show()

    def largeExt(self,path, gradeKey, hydrogenRange = 'low', FileErrorFlag = False):
        
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


                        if hydrogenRange == 'low':
                            OP = self.dataBrowser(self.df, '201 B', opIdx = 1)
                            PV = self.dataBrowser(self.df, '201 B')
                            PPM = self.dataBrowser(self.df, '201-1', '201 - 1', '201 -1')
                        elif hydrogenRange == 'high':
                            OP = self.dataBrowser(self.df, '202 B', opIdx = 1)
                            PV = self.dataBrowser(self.df, '202 B')
                            PPM = self.dataBrowser(self.df, '201-2', '201 - 2', '201 -2')
                        else:
                            OP = self.dataBrowser(self.df, 'A      B', opIdx = 1)
                            PV = self.dataBrowser(self.df, 'A      B')

                        mydict = {'OP': OP, 'PV': PV, 'PPM': PPM}
                        self.dataPool(self.name + '.xlsx', **mydict)
                        
                        logging.info(filePath + 'self.name:-> INDEX {}'.format(self.n))
                        self.n += 3
                        
##                    self.dfGrade = pd.read_excel(filePath)
##                    grade = self.dataBrowser(self.dfGrade, 'GRADE PROD', searchObj = 'Grade')
##                    
##                    mydict = {'OP': grade, 'PV': grade, 'PPM': grade}
##                    self.dataPool(self.name + '.xlsx', **mydict)
##
##                    logging.info(filePath + ':-> INDEX {}'.format(self.n))
##                    self.n += 3
                    
                    
                elif '.' not in files:
                    print(self.n)
                    self.largeExt(path + '\\' + files, gradeKey, *args)
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
                # General
                FCrow = IdxKey[0][-1]
                FCcol = IdxKey[1][-1]
                # 201 2023,2024
##                FCrow = IdxKey[0][0]
##                FCcol = IdxKey[1][0]
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

gradeKey2161 = ['MAS 2161']
gradeKey2161 = ['MAS 2162']
gradeKey2158 = ['MAS-2158', 'MAS 2158', 'MAS2158', 'MAS - 2158']
gradeKey2159 = ['MAS-2159', 'MAS 2159', 'MAS2159', 'MAS~2159']
gradeKey3355 = ['MAS-3355', 'MAS 3355', 'MAS3355', 'MAS~3355']
gradeKey3352 = ['MAS-3352', 'MAS 3352', 'MAS3352', 'MAS~3352']
gradeKey2345 = ['MAS-2345', 'MAS 2345', 'MAS2345', 'MAS~2345']

gradeKeyLow = gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

gradeKey5637 = ['MAS-5637', 'MAS 5637', 'MAS5637', 'MAS~5637']
gradeKey5402 = ['MAS-5402', 'MAS 5402', 'MAS5402', 'MAS~5402']
gradeKey7402 = ['MAS-7402', 'MAS 7402', 'MAS7402', 'MAS~7402']
gradeKey7702 = ['MAS-7702', 'MAS 7702', 'MAS7702', 'MAS~7702']

gradeKeyHigh = gradeKey5637 + gradeKey5402 + gradeKey7402 + gradeKey7702


##gradeKey_2008 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2010 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2012 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2014 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2016 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2018 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2019 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2020 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2021 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2022 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2023 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2024 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

myd = dataExt('FC201A_2023')
##myd.largeExt(r'D:\Polytama Propindo\Production - Documents\Bulk\Operations\2019\LST-2019\LST~1',gradeKey_2019,'FC201A_2019')

npd = myd.excelExt()
plots = myd.dataV(npd, secondData = False)

import sys
sys.path.append('../flakes')
import flakes
import numpy as np
import collections
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename = r'C:\Users\ssv\Documents\MRM\Exp\LargeDataExtractor\UserLogValveHigh_2023.log',level = logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode = 'a')

        
class dataExt():
    
    fl  = flakes.disturbance()
    
    def __init__(self, fileName):
        self.n = 1
        self.name = fileName
        self.excelSaveLoc = os.getcwd()
        
    def csvExt(self, path):
        y, _ = fl.modelDFile(path)
        fl.k = np.array([])
        x, _ = fl.modelDFile(path)
                                     
        mydict = dict(zip(FC202AKeys, FC202A))

        od = collections.OrderedDict(sorted(mydict.items()))
        del od[0]
        return y,x
    
    def excelExt(self, columnLimit=2, limit=800, fromFolder = False):
        """
        Default structure:
        column 1: valve opening
        column 2: flow value
        column 3: ppm hydrogen
        column n: additional parameters
        """
        path = self.excelSaveLoc + '/' + self.name + '.xlsx'
        if fromFolder == False:
            df = pd.read_excel(path)
            df = df.dropna(thresh =1).dropna(axis=1)
            df = df.sort_values(by=[df.columns.values[0]], ignore_index = True)
            df = df[df.iloc[:,columnLimit-2] > 0]
            df = df[df.iloc[:,columnLimit-2] < 100]
            df = df[df.iloc[:,columnLimit-1] > 0]
            df = df[df.iloc[:,columnLimit-1] < 2]
            df = df[df.iloc[:,columnLimit] > limit]
            npdata = df.values

            return npdata
        
    def dataV(self, npdata, secondData= True):

        fig, ax1 = plt.subplots()

        ax1.plot(npd[:,0], npd[:,1], linestyle = 'dashed',linewidth = 0.5, color = 'blue', label = self.name, marker = '.', markerfacecolor ='yellow', markersize = 7)
        ax1.set_xlabel('OP, %')
        ax1.set_ylabel('H2 kg/h', color = 'b')
        ax1.tick_params('y', colors='b')
        ax1.xaxis.set_major_locator(MultipleLocator(2))
##        ax1.yaxis.set_major_locator(MultipleLocator(0.025))

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines = lines1
        labels = labels1
        if secondData == True:
            ax2 = ax1.twinx()
            ax2.plot(npd[:,0], npd[:,2], label = 'PPM', linewidth = 0.5,color = 'red', linestyle ='dashed', marker ='.', markerfacecolor =  'yellow', markersize = 7)
            ax2.set_ylabel('PPM', color='r')
            ax2.tick_params('y', colors = 'r')
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines = lines1 + lines2
            labels = labels1 + labels2

        plt.legend(lines, labels, loc = 'upper right')
        plt.title(f'{self.name} Valve Trend', fontsize = 16, fontweight = 'bold')
        plt.show()
        
    def largeExt(self,path, gradeKey, hydrogenRange = 'R201', FileErrorFlag = False):
        
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


                        if hydrogenRange == 'R201':
                            OP = self.dataBrowser(self.df, '201 B', opIdx = 1)
                            PV = self.dataBrowser(self.df, '201 B')
                            PPM = self.dataBrowser(self.df, '201-1', '201 - 1', '201 -1')
                        elif hydrogenRange == 'R202':
                            OP = self.dataBrowser(self.df, '202 B', opIdx = 1)
                            PV = self.dataBrowser(self.df, '202 B')
                            PPM = self.dataBrowser(self.df, '201-2', '201 - 2', '201 -2')
                        elif hydrogenRange == 'R201NEW' :
                            OP = self.dataBrowser(self.df, 'A      B', opIdx = 1)
                            PV = self.dataBrowser(self.df, 'A      B')
                            PPM = self.dataBrowser(self.df, '201-1', '201 - 1', '201 -1')
##                        elif hydrogenRange == 'R202NEW' :
##                            OP = self.dataBrowser(self.df, 'A      B', opIdx = 1)
##                            PV = self.dataBrowser(self.df, 'A      B')
##                            PPM = self.dataBrowser(self.df, '201-2', '201 - 2', '201 -2')
##
                        mydict = {'OP': OP, 'PV': PV, 'PPM': PPM}
                        self.dataPool(self.name + '.xlsx', **mydict)
                        
                        logging.info(filePath + 'self.name:-> INDEX {}'.format(self.n))
                        self.n += 3
                        
##                    self.dfGrade = pd.read_excel(filePath)
##                    grade = self.dataBrowser(self.dfGrade, 'GRADE PROD', searchObj = 'Grade')
##                    
##                    mydict = {'OP': grade, 'PV': grade, 'PPM': grade}
##                    self.dataPool(self.name + '.xlsx', **mydict)
##
##                    logging.info(filePath + ':-> INDEX {}'.format(self.n))
##                    self.n += 3
                    
                    
                elif '.' not in files:
                    print(self.n)
                    self.largeExt(path + '\\' + files, gradeKey)
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
                # General
                FCrow = IdxKey[0][-1]
                FCcol = IdxKey[1][-1]
                # 201 2023,2024
##                FCrow = IdxKey[0][0]
##                FCcol = IdxKey[1][0]
                
##                FCrow = IdxKey[0][0]
##                FCcol = IdxKey[1][0]
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

gradeKey2161 = ['MAS 2161']
gradeKey2161 = ['MAS 2162']
gradeKey2158 = ['MAS-2158', 'MAS 2158', 'MAS2158', 'MAS - 2158']
gradeKey2159 = ['MAS-2159', 'MAS 2159', 'MAS2159', 'MAS~2159']
gradeKey3355 = ['MAS-3355', 'MAS 3355', 'MAS3355', 'MAS~3355']
gradeKey3352 = ['MAS-3352', 'MAS 3352', 'MAS3352', 'MAS~3352']
gradeKey2345 = ['MAS-2345', 'MAS 2345', 'MAS2345', 'MAS~2345']

gradeKeyLow = gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

gradeKey5637 = ['MAS-5637', 'MAS 5637', 'MAS5637', 'MAS~5637']
gradeKey5402 = ['MAS-5402', 'MAS 5402', 'MAS5402', 'MAS~5402']
gradeKey7402 = ['MAS-7402', 'MAS 7402', 'MAS7402', 'MAS~7402']
gradeKey7702 = ['MAS-7702', 'MAS 7702', 'MAS7702', 'MAS~7702']

gradeKeyHigh = gradeKey5637 + gradeKey5402 + gradeKey7402 + gradeKey7702


##gradeKey_2008 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2010 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2012 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2014 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2016 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2018 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2019 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2020 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2021 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2022 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2023 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345
##gradeKey_2024 = gradeKey2158 + gradeKey2161 + gradeKey2159 + gradeKey3355 + gradeKey3352 + gradeKey2345

myd = dataExt('FC201B_2023')
myd.largeExt(r'D:\Polytama Propindo\Production - Documents\Bulk\Operations\2023\LIST-2023\LST ~ 1',gradeKeyHigh)

##npd = myd.excelExt()
##plots = myd.dataV(npd, secondData = True)
