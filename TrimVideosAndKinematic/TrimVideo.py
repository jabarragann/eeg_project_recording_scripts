import pandas as pd
import numpy as np
import pyxdf
import cv2

if __name__  == '__main__':

    df = pd.read_csv('./UI08-T1-video_left_color_ts.txt',sep=',')

    df['ts'] = df['ts'] / 1e9

    data, header = pyxdf.load_xdf('./EX1U08_S01_T01_pegNormal_raw.xdf')
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

    start_time = float(markers[0][1])
    end_time   = float(markers[1][1])

    df = df.loc[(df['ts'] > start_time) & (df['ts'] < end_time)]
    x = 0
    start_frame = df['idx'].values[0]
    end_frame = df['idx'].values[-1]

    cap = cv2.VideoCapture('./video_left_color.avi')

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    outL = cv2.VideoWriter('out.avi', fourcc, 30, (640, 480))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame - 1)
    res = True
    while res:
        res, frame = cap.read()

        if res:
            cv2.imshow('video',frame)

            cv2.waitKey(1)
            outL.write(frame)

        start_frame += 1
        if start_frame == end_frame+1:
            res=False

    outL.release()

