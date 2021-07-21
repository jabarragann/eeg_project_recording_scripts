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
from _phase3_arithmetic_calibration.RegexFunctions import get_information2, get_information, get_information3

dataPath  = Path('./data_raw/')

def crop_df_with_markers(df, markers, markersTime):
    df = df.loc[(df['LSL_TIME'] > markersTime[0]) & (df['LSL_TIME'] < markersTime[1])]

    return df

def get_columns(stream):
    listOfChannels = stream['info']['desc'][0]['channels'][0]['channel']
    columns = []
    for ch in listOfChannels:
        try:
            columns.append(ch['label'][0])
        except:
            columns.append(ch['name'][0])
    return columns

def extract_eye_data(stream_dict,markers,markersTime, basePath):
    # Difference of LSL time and computer time
    difference = float(markers[0][1]) - markersTime[0]

    for e in ['left','right']:
        stream = stream_dict[e]
        data = stream['time_series']
        timestamps = stream['time_stamps']
        columns = get_columns(stream)
        df = pd.DataFrame(data=data, index=None, columns=columns)
        df["LSL_TIME"] = timestamps
        df = crop_df_with_markers(df,markers,markersTime)
        df.to_csv(basePath + 'eye_data_{:}.txt'.format(e))

def extract_gaze_position(stream, markers,markersTime,basePath):
    # Difference of LSL time and computer time
    difference = float(markers[0][1]) - markersTime[0]

    data = stream['time_series']
    timestamps = stream['time_stamps']
    columns = get_columns(stream)
    df = pd.DataFrame(data=data, index=None, columns=columns)
    df["LSL_TIME"] = timestamps
    df = crop_df_with_markers(df, markers, markersTime)
    df.to_csv(basePath + 'gaze_position.txt')

def main():
    for f in dataPath.glob('*.xdf'):

        # Load xdf files
        if len(re.findall(".xdf", f.name)) > 0:
            file = f

            uid, session, trial, task = get_information3(file)  # If any problem check the regex functions.
            # # Rename files --> remove identifiers
            # uid = re.findall('.+(?=_S[0-9]{1}_T[0-9]{3}_)', file.name)[0]
            # session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]{3}_)', file.name)[0])
            # trial = int(re.findall('(?<=_S[0-9]{1}_T)[0-9]+(?=_)', file.name)[0])
            # task = re.findall('(?<=_S[0-9]{1}_T[0-9]{3}_).+(?=_raw\.xdf)', file.name)[0]

            basePath = './eye_tracker_txt/' + "{:}_S{:02d}_T{:02d}_{:}_".format(uid, session, trial, task)

            print(uid, session, trial, task)
            print("srcPath", f)
            print("dstPath", basePath)

            data, header = pyxdf.load_xdf(file)
            stream_names = [stream['info']['name'][0] for stream in data]
            print(stream_names)

            eye_stream_dict = {}
            gaze_stream = None
            markers, markersTime = None, None

            # Get data and experiment markers
            for stream in data:
                if stream['info']['name'][0] == 'left_eye_data' or stream['info']['name'][0] == 'right_eye_data':
                    eye = 'left' if 'left' in stream['info']['name'][0] else 'right'
                    eye_stream_dict[eye] = stream
                if stream['info']['name'][0] == 'gaze_position':
                    gaze_stream = stream
                if stream['info']['name'][0] == 'ExperimentMarkers':
                    if stream['time_series'][0][0] == '':
                        continue
                    markers = stream['time_series']
                    markersTime = stream['time_stamps']

            extract_eye_data(eye_stream_dict, markers, markersTime, basePath)
            extract_gaze_position(gaze_stream, markers, markersTime, basePath)



if __name__ == "__main__":

   main()