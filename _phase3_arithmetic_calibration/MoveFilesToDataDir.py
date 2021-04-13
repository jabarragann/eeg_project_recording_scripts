import re
from pathlib import Path
import shutil

if __name__ == "__main__":

    src_path = Path("./").resolve()
    dst_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments3-Data\CalibrationProcedure-NeedlePasssingBlood')

    for p,dst_2 in [('data_edf','edf'),('data_raw','raw'),('data_txt','txt'),('eye_tracker_txt','eyetracker')]:
        p2 = src_path/p

        print(p)
        for file in p2.rglob("*"):
            uid = re.findall('.+(?=_S[0-9]+_T[0-9][0-9]_)', file.name)[0][1:]
            session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9][0-9]_)', file.name)[0])

            dst_final_final = dst_path / dst_2 / uid / "S{:02d}".format(session)

            print("move ", file.name)
            print("to ", dst_final_final)
            if  not dst_final_final.exists():
                dst_final_final.mkdir(parents=True)

            try:
                shutil.move(str(file), str(dst_final_final))
            except shutil.Error:
                print("dst already exists!")