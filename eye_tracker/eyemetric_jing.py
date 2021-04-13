# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 16:46:52 2021

@author: yangj
"""
import numpy as np
import pandas as pd
class fixation_dector:
    def __init__(self, eyeright, eyeleft,time):
        self.eyeleft = np.array(eyeleft)
        self.eyeright = np.array(eyeright)
        self.time = np.array(time)
        
    def remove_missing(self,missing=0):
        mx = np.array(np.array(self.eyeleft) == missing, dtype = int)
        my = np.array(np.array(self.eyeright) == missing, dtype = int) 
        self.eyeleft = self.eyeleft[ (my + mx) != 2]
        self.eyeright = self.eyeright[ (my + mx) != 2]
        self.time = self.time[(mx+my) !=2]
        return self.eyeleft, self.eyeright, self.time
    def fixation_dection(self,mindur=85):
        x,y,time = self.remove_missing(missing=0)
        Sfix=[]
        Efix=[]
        si=0
        fixationstart=False
        for i in range(1,len(x)):
            try:
                gap = np.abs(int((time[i-1]-time[i])))
                if gap <=mindur and not fixationstart:
                    fixationstart=True
                    Sfix.append(time[i])                        
                if gap>mindur and fixationstart:
                    fixationstart=False
                    Efix.append([Sfix[-1],time[i-1],int(time[i-1]-Sfix[-1]),x[i],y[i]])
            except KeyError:
                pass
        return Efix

    def fixation_distance(self,a,b):
        dis=np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        return dis 
    def sp_calculation(self, fixationposition):
        scanpth=0
        for i in range(0,len(fixationposition)-1):
            scanpth = self.fixation_distance(fixationposition[i+1], fixationposition[i])+scanpth
        return scanpth
    def scanpath_eye(self,mindur=85):
        fixation = self.fixation_dection(mindur)
        df = pd.DataFrame(data=fixation, columns = ['starttime','endtime', 'duration',
                                                    'posx', 'posy'])
        sp = self.sp_calculation(np.array(df[['posx','posy']]))
        return sp
        
    
    
     
    
    
                    
                
    
        
        
        
        