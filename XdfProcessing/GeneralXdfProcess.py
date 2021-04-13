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
import json


if __name__ == "__main__":

    file  = Path('./data/UDani_S05_T01_validationbloodcountinously_raw.xdf')
    dst_path = Path('./results/') / file.with_suffix("").name

    if not dst_path.exists():
        dst_path.mkdir(parents=True)

    data, header = pyxdf.load_xdf(file)

    stream_names = [stream['info']['name'][0] for stream in data]
    print(stream_names)

    for stream in data:
        stream_name = stream['info']['name'][0]
        stream_info = stream['info']
        time_series = np.array(stream['time_series']) #Recorded values
        time_stamps = np.array(stream['time_stamps']).reshape(-1,1) #Timestamps

        data = np.hstack((time_stamps,time_series))
        df = pd.DataFrame(data)
        df.to_csv(dst_path / "{:}_data.csv".format(stream_name) ,index=False)

        with open(dst_path / "{:}_info.json".format(stream_name),'w') as f1:
            json_data = json.dumps(stream_info,indent=3)
            f1.write(json_data)

    # workloadPredData = None; workloadPredInfo = None; workloadPredTime = None
    # #Get data and experiment markers
    # #Remake this method to be more general ** Later today
    # #Also adjust the code so that each signal is trimmed from data that does not belongs to experiment
    # #Finally normalize by the time when the experiment started
    # for stream in data:
    #     if stream['info']['name'][0] == 'ExperimentMarkers':
    #         if stream['time_series'][0][0] == '':
    #             continue
    #         markers = stream['time_series']
    #         markersTime = stream['time_stamps']
    #     elif stream['info']['name'][0] == 'NB-2015.10.15' or stream['info']['name'][0] == 'NB-2015.10.16':
    #         # if stream['footer']['info']['first_timestamp'][0] != '0':
    #         eegData = stream['time_series']
    #         eegInfo = stream['info']
    #         eegTime = stream['time_stamps']
    #     elif stream['info']['name'][0] == 'PredictionEvents':
    #         workloadPredData = np.array(stream['time_series'])
    #         workloadPredInfo = stream['info']
    #         workloadPredTime = stream['time_stamps']
    #     elif stream['info']['name'][0] == 'AlarmEvents':
    #         alarmPredData = np.array(stream['time_series'])
    #         alarmPredInfo = stream['info']
    #         alarmPredTime = stream['time_stamps']
    #
    # if len( markers ) > 2: #If multiple events are found in the recording only grab the last two
    #     markers = markers[-2:]
    #     markersTime = markersTime[-2:]
    #
    # if task != "Baseline":
    #     #Crop predictions and events with start and end signals
    #     valIdx = (alarmPredTime > markersTime[0]) & (alarmPredTime < markersTime[1])
    #     alarmPredData =  alarmPredData[valIdx]
    #     alarmPredTime = alarmPredTime[valIdx] - markersTime[0]
    #     valIdx = (workloadPredTime > markersTime[0]) & (workloadPredTime < markersTime[1])
    #     workloadPredData = workloadPredData[valIdx]
    #     workloadPredTime = workloadPredTime[valIdx] - markersTime[0]
    #
    #     #Save predictions
    #     alarmDict = dict(data=alarmPredData, time=alarmPredTime )
    #     predDict = dict(data=workloadPredData,time = workloadPredTime)
    #     finalDict = dict(alarm=alarmDict, pred=predDict)
    #     p1 = './prediction_events/' + f.with_suffix("").name + "_intervention.pickle"
    #     pickle.dump(finalDict,open(p1,'wb'))
    #
    # #Difference of LSL time and computer time
    # difference = float(markers[0][1]) - markersTime[0]
    #
    # #Get EEG headers
    # columns = []
    # listOfChannels = eegInfo['desc'][0]['channels'][0]['channel']
    # for ch in listOfChannels:
    #     try:
    #         columns.append(ch['label'][0])
    #     except:
    #         columns.append(ch['name'][0])
    #
    # columns = [x.upper() for x in columns]
    # eegChannels = copy.deepcopy(columns)
    # #eegChannels.remove("COUNTER")
    #
    # #Create data frame
    # df =  pd.DataFrame(data=eegData, index=None, columns=columns)
    #
    #
    # #Add label and time stamps
    # df['LSL_TIME'] = eegTime
    #
    # #Label
    # if task == "Baseline" or task == 'BASELINE': #Baseline
    #     df['label'] = 0
    # elif task == "Normal" or task == "Easy" or task == 'Low' or task == 'LOW': #Low Workload
    #     df['label'] = 5
    # elif task == "Inv" or task =='inv' or task == "High" or task == 'HIGH': # high Workload
    #     df['label'] = 10
    #
    # #Remove data before start and after finish
    # df = df.loc[(df['LSL_TIME'] > markersTime[0]) & (df['LSL_TIME'] < markersTime[1]) ]
    #
    # #Update timestamps to computer time
    # df['COMPUTER_TIME'] = df['LSL_TIME'] + difference
    #
    # df['LSL_TIME']= df['LSL_TIME'] - markersTime[0]
    # print(len(df['COMPUTER_TIME']))
    # #Save to CSV
    #
    # df.to_csv(dstPath,index=None)
