from pathlib import Path
import re
import pyxdf
import numpy as np
import json
import pandas as pd

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

def get_information(file):
    uid = re.findall('.+(?=_S[0-9]+_T[0-9]{3}_)', file.name)[0]
    session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]{3})', file.name)[0])
    trial = int(re.findall('(?<=_S[0-9]{1}_T)[0-9]{3}(?=_)', file.name)[0])
    task = re.findall('(?<=_S[0-9]{1}_T[0-9]{3}_).+(?=\.xdf)', file.name)[0]

    return uid, session, trial, task

def get_information2(file):
    uid = re.findall('.+(?=_SRE+_T[0-9]{3}_)', file.name)[0]
    session = "RE"
    trial = int(re.findall('(?<=_SRE_T)[0-9]{3}(?=_)', file.name)[0])
    task = re.findall('(?<=_SRE_T[0-9]{3}_).+(?=\.xdf)', file.name)[0]

    return uid, session, trial, task

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
    src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\raw')
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\expanded')

    for file in src_path.rglob("*.xdf"):
        if 'experiment01' in file.name:

            try:
                uid, session, trial, task = get_information2(file)
            except Exception:
                continue

            print(file)
            print(uid, session, trial, task)

            new_p = dst_path / uid / "T{:02d}_{:}".format(trial, task)

            expand_files(file,new_p)

if __name__ == "__main__":

   main()