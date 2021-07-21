from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from _phase3_arithmetic_calibration.RegexFunctions import get_information, get_information3

def main():
    # src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\raw')
    # dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\expanded')
    # metrics_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments5-realtime-needle-pass\metrics\real-time-plots')

    # src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments\raw')
    # dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments\expanded')
    # metrics_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments\metrics\real-time-plots')

    src_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData\raw')
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData\expanded')
    metrics_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData\metrics\real-time-plots')

    for file in src_path.rglob("*.xdf"):
            if 'experiment01' in file.name and 'realtime' in file.name or True:
                if not metrics_path.exists():
                    metrics_path.mkdir(parents=True)

                try:
                    uid, session, trial, task = get_information3(file)
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