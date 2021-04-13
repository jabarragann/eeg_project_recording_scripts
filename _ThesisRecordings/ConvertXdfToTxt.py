import random
import pyxdf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import copy
from pathlib import Path
from pylsl import local_clock
import time
import pickle

dataPath  = Path('./data_raw/')

for f in dataPath.glob('*.xdf'):

    #Load xdf files
    if len(re.findall(".xdf", f.name))>0:
        file = f

        # Rename files --> remove identifiers
        uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', file.name)[0]
        session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]{2}_)', file.name)[0])
        trial = int(re.findall('(?<=_S[0-9]{2}_T)[0-9]+(?=_)', file.name)[0])
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.xdf)', file.name)[0]

        dstPath = Path('./data_txt/') / "{:}_S{:02d}_T{:02d}_{:}_raw.txt".format(uid, session, trial, task)

        print(uid, session, trial, task)
        print("srcPath", f)
        print("dstPath", dstPath)


        data, header = pyxdf.load_xdf(file)

        stream_names = [stream['info']['name'][0] for stream in data]
        print(stream_names)

        workloadPredData = None; workloadPredInfo = None; workloadPredTime = None
        #Get data and experiment markers
        #Remake this method to be more general ** Later today
        #Also adjust the code so that each signal is trimmed from data that does not belongs to experiment
        #Finally normalize by the time when the experiment started
        for stream in data:
            if stream['info']['name'][0] == 'ExperimentMarkers':
                if stream['time_series'][0][0] == '':
                    continue
                markers = stream['time_series']
                markersTime = stream['time_stamps']
            elif stream['info']['name'][0] == 'NB-2015.10.15' or stream['info']['name'][0] == 'NB-2015.10.16':
                # if stream['footer']['info']['first_timestamp'][0] != '0':
                eegData = stream['time_series']
                eegInfo = stream['info']
                eegTime = stream['time_stamps']
            elif stream['info']['name'][0] == 'PredictionEvents':
                workloadPredData = np.array(stream['time_series'])
                workloadPredInfo = stream['info']
                workloadPredTime = stream['time_stamps']
            elif stream['info']['name'][0] == 'AlarmEvents':
                alarmPredData = np.array(stream['time_series'])
                alarmPredInfo = stream['info']
                alarmPredTime = stream['time_stamps']

        #Get Mouse Buttons indicating begining and end of experiment
        # markers = np.array(markers).reshape(-1,)
        # idx = np.where(markers == "MouseButtonX2 pressed")
        # markers = markers[idx]
        # markersTime = markersTime[idx]
        #
        # if len( markers ) > 2:
        #     print("Check mouse markers! there should only be two events here!")
        #     exit(0)


        #Difference of LSL time and computer time
        difference = float(markers[0][1]) - markersTime[0]

        #Get EEG headers
        columns = []
        listOfChannels = eegInfo['desc'][0]['channels'][0]['channel']
        for ch in listOfChannels:
            try:
                columns.append(ch['label'][0])
            except:
                columns.append(ch['name'][0])

        columns = [x.upper() for x in columns]
        eegChannels = copy.deepcopy(columns)
        #eegChannels.remove("COUNTER")

        #Create data frame
        df =  pd.DataFrame(data=eegData, index=None, columns=columns)


        #Add label and time stamps
        df['LSL_TIME'] = eegTime

        #Remove data before start and after finish
        df = df.loc[(df['LSL_TIME'] > markersTime[0]) & (df['LSL_TIME'] < markersTime[1]) ]


        #Update timestamps to computer time
        df['COMPUTER_TIME'] = df['LSL_TIME'] + difference

        df['LSL_TIME']= df['LSL_TIME'] - markersTime[0]
        print(len(df['COMPUTER_TIME']))
        #Save to CSV

        df.to_csv(dstPath,index=None)
