import numpy as np
import pandas as pd

df_data = pd.read_excel(r"D:\Polytama Propindo\Production - Documents\Bulk\Operations\2024\BULK\08~AUG\BL_14.xlsx")
print(df_data)
print(df_data.iloc[33,15])

def collector(xpoint_init, ypoint_init, xstep, ystep, xorient, yorient):
    db = []
    xstepper = []
    ystepper = []
    for i in range(xorient):
        xstepper.append(xpoint_init)
        xpoint_init += xstep
        
    for j in range(yorient):
        ystepper.append(ypoint_init)
        ypoint_init += ystep
        
    for i in ystepper:
        dp = df_data.iloc[i, i]
        
        for j in xstepper:
            dp = df_data.iloc[j,i]
            db.append(dp)

    return db

collector(33,15,1,3,2,4)

    
