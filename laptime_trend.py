# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 09:29:45 2023

@author: mvvsk
"""

import fastf1 as ff1
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np 

pd.options.mode.chained_assignment = None
ff1.Cache.enable_cache('cache/')

session = ff1.get_session(2023, "Canada", 'RACE')
session.load(telemetry=False, weather=False)
delete_laps=[1,2,3]
laptimemin, laptimemax = 75, 79
drvs=['VER','HAM']

col_dict={
    "PER":"Blue",
    "VER":"Blue",
    "LEC":"Red",
    "SAI":"Red",
    "RUS":"Cyan",
    "HAM":"Cyan",
    "ALO":"Green",
    "STR":"Green",
    "PIA":"#ff8700",
    "NOR":"#ff8700",
    "ALB":"#005aff",
    "SAR":"#005aff",
    "GAS":"#0090ff",
    "OCO":"#0090ff",
    "HUL":"#ffffff",
    "MAG":"#ffffff",
    "TSU":"#2b4562",
    "DEV":"#2b4562",
    "BOT":"#900000",
    "ZHO":"#900000",
    }

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(19.20, 10.8), dpi=100)

for drv in drvs:
    drv_laps=session.laps.pick_driver(drv)
    abb = drv_laps['Driver'].iloc[0]
    drv_col=col_dict[drv]
    LN=drv_laps['LapNumber'].tolist()
    Lap_tym=drv_laps['LapTime'].dt.total_seconds().tolist()
    Comp=drv_laps['Compound'].tolist()
    cols=[]
    for C in Comp:
        if C=='MEDIUM':
            cols.append('Yellow')
        if C=='HARD':
            cols.append('White')
        if C=='SOFT':
            cols.append('Red')
    df=pd.DataFrame(list(zip(LN, Lap_tym,Comp,cols)),
               columns =['LapNumber', 'LapTime','Compound','TyreColor'])
    # Filter Based on Laptimes
    df=df[df['LapTime']>laptimemin]
    df=df[df['LapTime']<laptimemax]
    
    # Delete laps
    for L in delete_laps:
        df2=df.drop(df[df['LapNumber']==L].index, inplace = True)
    
    x=df['LapNumber']
    y=df['LapTime']
    xnew = np.linspace(df['LapNumber'].min(), df['LapNumber'].max(), 
                       num=3*len(df['LapNumber']), endpoint=True)
    f_cubic = interp1d(x, y, kind=3)
    
    ax.plot(df['LapNumber'],df['LapTime'],linewidth=3, label=abb, color=drv_col)
    # ax.plot(xnew,f_cubic(xnew),label=abb, color=drv_col)
    ax.scatter(x=x,y=y,s=100,c=df['TyreColor'],edgecolor=drv_col)

ax.set_ylim([laptimemin,laptimemax])
ax.set_ylabel('Lap Time, s',fontsize=26)
ax.set_xlabel('Lap Number',fontsize=26)
ax.xaxis.set_tick_params(labelsize=25)
ax.yaxis.set_tick_params(labelsize=25)
ax.legend(bbox_to_anchor=(1.0, 1.02),fontsize='32')
plt.suptitle(
    f" Lap Time Trend \n"
    f"{session.event.year} {session.event['EventName']} (RACE) ", fontsize=25, fontweight='bold')
resolution_value = 100

# Turn on major grid lines
plt.grid(color='w', which='major', axis='both', linestyle='--')
plt.tight_layout()

plt.show()    