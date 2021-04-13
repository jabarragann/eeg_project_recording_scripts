from pathlib import Path
import re
import pyxdf
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt

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

def main():
    src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\raw')
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\expanded')
    metrics_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\metrics\real-time-plots')

    for file in src_path.rglob("*.xdf"):
            if 'experiment01' in file.name and 'realtime' in file.name:

                try:
                    uid, session, trial, task = get_information2(file)
                except Exception:
                    continue

                print(file)
                print(uid, session, trial, task)

                new_p = dst_path / uid / "T{:02d}_{:}".format(trial, task)

                #Dataframes
                assistant_state_df = new_p / "AssistantState_data.csv"
                assistant_state_df  = pd.read_csv(assistant_state_df)
                predictions_df = new_p / "PredictionEvents_data.csv"
                predictions_df = pd.read_csv(predictions_df)

                init_time = predictions_df.iloc[0,0]
                fig, ax = plt.subplots(1,1,figsize=(15,5))
                plt.plot(predictions_df['0']-init_time, predictions_df['1'])
                plt.title(uid + " " + new_p.name)
                ax.set_xlabel("time (s)")
                ax.set_ylabel("Workload index")
                ax.set_ylim((0,1))
                ax.set_xlim((-10,730))
                ax.grid()
                #plot suction events
                for i in range(assistant_state_df.shape[0]):
                    if assistant_state_df.iloc[i,1] == 'Suction':
                        ax.axvline(assistant_state_df.iloc[i,0]-init_time, color='black')
                plt.tight_layout()
                plt.savefig(metrics_path / (uid + "T{:02d}_{:}".format(trial, task)) )
                # plt.show()
                plt.close(fig)

if __name__ == "__main__":

   main()