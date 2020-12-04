from pathlib import Path
import os
import re
from shutil import copyfile

if __name__ == "__main__":

    rootPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments3-Data\CalibrationProcedure-SurgicalTasks")
    videoPath = rootPath / "videos"
    eegPath = rootPath / "txt"

    newPath = rootPath / "test_videos"
    if not newPath.exists():
        newPath.mkdir()

    #Renaming the files
    for video_file in videoPath.rglob("*.avi"):

        uid = re.findall('.+(?=_S[0-9][0-9]+_T[0-9][0-9]_)', video_file.name)[0]
        session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9][0-9]_)', video_file.name)[0])
        trial = int(re.findall('(?<=_S[0-9]{2}_T)[0-9]{2}(?=_)', video_file.name)[0])
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw)', video_file.name)[0]

        print(uid, session, trial, task)
        parts = video_file.with_suffix('').name.split("_")
        ts_file = videoPath / ("_".join(parts[:7]) + "_ts.txt")
        eeg_file = eegPath / uid/ ("_".join(parts[:5]) + ".txt")

        print(video_file)
        print(ts_file, ts_file.exists())
        print(eeg_file, ts_file.exists())

        dstPath = newPath / uid / "_".join(parts[1:4])
        print(dstPath)

        if not dstPath.exists():
            dstPath.mkdir(parents=True)

        copyfile(eeg_file, dstPath/eeg_file.name)
        copyfile(ts_file,  dstPath/ts_file.name)
        copyfile(video_file,  dstPath/video_file.name)
    #
    # #Renaming the files
    # for file in os.listdir(path):
    #     print(file)
    #     parts = file.split("_")
    #     print(parts)
    #     new_name = "_".join(parts[:4]) + "_raw_" + "_".join(parts[4:])
    #     print(new_name)
    #     os.rename(path/file, path/new_name)