
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

#Calculate difference between LSL clock and computer clock
t1 = local_clock()
t2 = time.time()
difference = t2 - t1


dataPath  = Path('./data/')

for f in dataPath.glob('*.xdf'):
    print(f)
    #Load xdf files
    if len(re.findall(".xdf", f.name))>0:
        file = f

        task = re.findall("(?<=T[0-9]{3}_).+(?=\.xdf)", file.name)[0]
        subject =  re.findall(".+(?=_S[0-9]{3})", file.name)[0]
        session =  int(re.findall("(?<=_S)[0-9]{3}(?=_T)", file.name)[0])
        trial =  int(re.findall("(?<=_T)[0-9]{3}(?=_)", file.name)[0])

        dstPath = Path('./data-processed/') / "{:}_S{:d}_T{:d}_{:}.txt".format(subject,session, trial,task)
        data, header = pyxdf.load_xdf(file)

        #Get data and experiment markers
        for stream in data:
            if stream['info']['name'][0] == 'ExperimentMarkers':
                markers = stream['time_series']
                markersTime = stream['time_stamps']
            elif stream['info']['name'][0] == 'NB-2015.10.15' or stream['info']['name'][0] == 'NB-2015.10.16':
                eegData = stream['time_series']
                eegInfo = stream['info']
                eegTime = stream['time_stamps']

        #Get EEG headers
        columns = []
        listOfChannels = eegInfo['desc'][0]['channels'][0]['channel']
        for ch in listOfChannels:
            columns.append(ch['label'][0])

        columns = [x.upper() for x in columns]
        eegChannels = copy.deepcopy(columns)
        #eegChannels.remove("COUNTER")

        #Create data frame
        df =  pd.DataFrame(data=eegData, index=None, columns=columns)

        #Add label and time stamps
        df['COMPUTER_TIME'] = eegTime
        df['label'] = 5 if task == 'Normal' else  10

        #Remove data before start and after finish
        df = df.loc[(df['COMPUTER_TIME'] > markersTime[0]) & (df['COMPUTER_TIME'] < markersTime[1]) ]

        #Update timestamps to computer time
        df['COMPUTER_TIME'] = df['COMPUTER_TIME'] + difference

        #Save to CSV

        df.to_csv(dstPath,index=None)

    # channel = random.choice(eegChannels)
    # plt.plot(df['COMPUTER_TIME']-markersTime[0],df[channel], label = channel)
    # plt.legend()
    #
    # for timestamp, marker in zip(markersTime, markers):
    #     plt.axvline(x=timestamp - markersTime[0], color = 'black')
    #     #print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
    #
    # plt.show()