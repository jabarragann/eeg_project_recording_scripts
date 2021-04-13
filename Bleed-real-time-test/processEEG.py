
import pandas as pd
import re
import copy
from pathlib import Path
import pyxdf
from pylsl import local_clock
import time

if __name__ == '__main__':
    path = "./lowTrial"
    #extract the video of interest
    tsVideo = pd.read_csv(path + "/video_left_color_ts.txt", sep=',')
    tsVideo = tsVideo[['ecm_ts','ecm_idx']]
    tsVideo['ecm_ts'] = tsVideo['ecm_ts'] / 1e9

    tsFile = tsVideo.copy()
    tsFile['ecm_ts'] = tsVideo['ecm_ts'] - tsVideo['ecm_ts'].values[0]

    #Load manually selected starting and ending points from the video
    select = pd.read_csv(path + "/selectedTimes.txt", index_col=0)
    videoStart = select.loc['start','min']*60 + select.loc['start','sec']
    videoEnd   = select.loc['end','min']*60 +  select.loc['end','sec']

    # videoStart = select.iloc['start'][0] * 60 + 51.978
    # videoEnd = 9 * 60 + 50.350

    tsFile = tsFile.loc[(tsFile['ecm_ts'] > videoStart) & (tsFile['ecm_ts'] < videoEnd) ]
    tsVideo = tsVideo.iloc[tsFile.index.values]
    x = 0

    #Extract the eeg signals from video of interest
    dataPath = Path(path)
    experiment = 2
    for f in dataPath.glob('*.xdf'):
        print(f)
        # Load xdf files
        if len(re.findall(".xdf", f.name)) > 0:
            file = f

            task = re.findall("(?<=T[0-9]{2}_).+(?=\.)", file.name)[0]
            subject = re.findall(".+(?=_S[0-9]{2})", file.name)[0]
            session = int(re.findall("(?<=_S)[0-9]{2}(?=_T)", file.name)[0])
            trial = int(re.findall("(?<=_T)[0-9]{2}(?=_)", file.name)[0])

            dstPath = dataPath / "{:}_S{:d}_T{:d}_{:}_raw.txt".format(subject, session, trial, task)

            data, header = pyxdf.load_xdf(file)

            # Get data and experiment markers
            for stream in data:
                if stream['info']['name'][0] == 'ExperimentMarkers':
                    markers = stream['time_series']
                    markersTime = stream['time_stamps']
                elif stream['info']['name'][0] == 'NB-2015.10.15' or stream['info']['name'][0] == 'NB-2015.10.16':
                    if stream['footer']['info']['first_timestamp'][0] != '0':
                        eegData = stream['time_series']
                        eegInfo = stream['info']
                        eegTime = stream['time_stamps']

            # Get EEG headers
            columns = []
            listOfChannels = eegInfo['desc'][0]['channels'][0]['channel']
            for ch in listOfChannels:
                try:
                    columns.append(ch['label'][0])
                except:
                    columns.append(ch['name'][0])

            columns = [x.upper() for x in columns]
            eegChannels = copy.deepcopy(columns)
            # eegChannels.remove("COUNTER")

            # Create data frame
            df = pd.DataFrame(data=eegData, index=None, columns=columns)

            # Add label and time stamps
            df['COMPUTER_TIME'] = eegTime

            # Label
            if task == "Baseline" or task == 'BASELINE':  # Baseline
                df['label'] = 0
            elif task == "Normal" or task == "Easy" or task == 'Low' or task == 'LOW':  # Low Workload
                df['label'] = 5
            elif task == "Inv" or task == 'inv' or task == "High" or task == 'HIGH':  # high Workload
                df['label'] = 10

            # Remove data before start and after finish
            try:
                df = df.loc[(df['COMPUTER_TIME'] > markersTime[0]) & (df['COMPUTER_TIME'] < markersTime[1])]
            except:
                df = df.loc[(df['COMPUTER_TIME'] > markersTime[0])]


            # Update timestamps to computer time
            # Convert eeg ts from LSL time to local computer time to synchronize with video
            markerStartTime = float(markers[0][1])
            newEegTime = (df['COMPUTER_TIME'] - df['COMPUTER_TIME'].values[0]) + markerStartTime
            df['COMPUTER_TIME'] = newEegTime

            assert tsVideo.iloc[0, 0] - newEegTime.iloc[0] > 0, "Something went wrong!"  +\
            "The manually selected video start should be after the initial start signal of the eeg"

            assert tsVideo.iloc[-1, 0] - newEegTime.iloc[-1]<0 , "Something went wrong!" + \
                "The manually selected interval from the video should be fully contained in the eeg "+\
                "starting and ending signals."

            #Crop eeg signals with manually selected video start and end.
            df = df.loc[ (df['COMPUTER_TIME'] > tsVideo.iloc[0,0]) &  (df['COMPUTER_TIME'] < tsVideo.iloc[-1,0])]

            print("Total eeg time", df['COMPUTER_TIME'].iloc[-1] - df['COMPUTER_TIME'].iloc[0] )
            print("Total video time", tsVideo.iloc[-1,0]-tsVideo.iloc[0,0])

            df.to_csv(dstPath, index=None)
            tsVideo.to_csv(path+'/selectedVideoFrames.txt', index=None)

