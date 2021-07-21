from pathlib import Path
import pyxdf
import numpy as np
import json
import pandas as pd
from _phase3_arithmetic_calibration.RegexFunctions import  get_information, get_information3


def get_experimental_marker(data):
    # Get data and experiment markers
    for stream in data:
        if stream['info']['name'][0] == 'ExperimentMarkers':
            if stream['time_series'][0][0] == '':
                continue
            markers = stream['time_series']
            markersTime = stream['time_stamps']

            return markers, markersTime

    raise Exception("No experimental markers found")


def expand_files(file, dst_path):

    if not dst_path.exists():
        dst_path.mkdir(parents=True)

    data, header = pyxdf.load_xdf(file)

    stream_names = [stream['info']['name'][0] for stream in data]
    # print(stream_names)

    markers, markers_time = get_experimental_marker(data)

    for stream in data:
        stream_name = stream['info']['name'][0]
        stream_info = stream['info']
        time_series = np.array(stream['time_series']) #Recorded values
        time_stamps = np.array(stream['time_stamps']).reshape(-1,1) #Timestamps

        #Trim signals with experimental markers
        idx = np.where((time_stamps > markers_time[0]) & (time_stamps < markers_time[1]))
        time_series = time_series[idx].reshape(-1,1)
        time_stamps = time_stamps[idx].reshape(-1,1)

        data = np.hstack((time_stamps,time_series))
        df = pd.DataFrame(data)
        df.to_csv(dst_path / "{:}_data.csv".format(stream_name) ,index=False)

        with open(dst_path / "{:}_info.json".format(stream_name),'w') as f1:
            json_data = json.dumps(stream_info,indent=3)
            f1.write(json_data)

def main():
    # src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\raw')
    # dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\expanded')
    #src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-IU-experiments\raw')
    #dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-IU-experiments\expanded')

    src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData\raw')
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData\expanded')
    # src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments\raw')
    # dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments\expanded')

    for file in src_path.rglob("*.xdf"):
        #print(file)
        if 'experiment01' in file.name or True:

            try:
                uid, session, trial, task = get_information3(file)
            except Exception as e:
                print(e)
                continue

            print(file)
            print(uid, session, trial, task)

            new_p = dst_path / uid / "T{:02d}_{:}".format(trial, task)

            expand_files(file,new_p)

if __name__ == "__main__":

   main()