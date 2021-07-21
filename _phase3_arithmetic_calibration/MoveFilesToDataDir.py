import re
from pathlib import Path
import shutil
from _phase3_arithmetic_calibration.RegexFunctions import get_information,get_information2
if __name__ == "__main__":

    src_path = Path("./").resolve()
    #dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-IU-experiments')
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\MasterThesisExperiment\SensorsData')
    #dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Realtime-Project-Purdue-experiments')

    for p,dst_2 in [('data_edf','edf'),('data_raw','raw'),('data_txt','txt'),('eye_tracker_txt','eyetracker'),('video_trimmed','video_trimmed')]:
        p2 = src_path/p

        print(p)
        for file in p2.rglob("*"):
            uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', file.name)[0][1:]
            session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]+_)', file.name)[0])

            dst_final_final = dst_path / dst_2 / uid / "S{:02d}".format(session)

            print("move ", file.name)
            print("to ", dst_final_final)
            if  not dst_final_final.exists():
                dst_final_final.mkdir(parents=True)

            try:
                shutil.move(str(file), str(dst_final_final))
            except shutil.Error:
                print("dst already exists!")