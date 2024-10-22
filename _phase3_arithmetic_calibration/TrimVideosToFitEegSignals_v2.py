"""
Use this for any file structure
"""

import cv2
import numpy as np
from pathlib import Path
import pandas as pd
import re
from _phase3_arithmetic_calibration.RegexFunctions import get_information2, get_information

def trimVideoToSignals(new_video_path, new_ts_path, video_path, ts_path, eeg_file_path, show=False):
    ts_file = pd.read_csv(ts_path)
    ts_file["ecm_ts"] = ts_file["ecm_ts"] * 1e-9
    eeg_file = pd.read_csv(eeg_file_path)

    # Identify frames before starting signal and after ending
    frames_before = ts_file.loc[ts_file["ecm_ts"] < eeg_file.loc[0, "COMPUTER_TIME"]]
    initial_frames_to_remove = frames_before.shape[0]
    # Starting frames
    frames_after = ts_file.loc[ts_file["ecm_ts"] > eeg_file["COMPUTER_TIME"].values[-1]]
    ending_frames_to_remove = frames_after.shape[0]
    # Ending frames
    trimmed_ts_file = ts_file.loc[(ts_file["ecm_ts"] > eeg_file.loc[0, "COMPUTER_TIME"]) &
                                  (ts_file["ecm_ts"] < eeg_file["COMPUTER_TIME"].values[-1])]
    trimmed_ts_file.to_csv(new_ts_path)

    final_video_size = trimmed_ts_file.shape[0]
    print("Removed frames at the start {:d} and at the end {:d}".format(initial_frames_to_remove,
                                                                        ending_frames_to_remove))
    print("Final video size {:d}".format(final_video_size))

    # Open video
    cap = cv2.VideoCapture(str(video_path))
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Frames in video {:d}, frames in ts file {:d}".format(total_frame_count, ts_file.shape[0]))
    cap.set(cv2.CAP_PROP_POS_FRAMES, initial_frames_to_remove)  # skip all the initial frames

    # Output video
    frame_width = 640
    frame_height = 480
    out = cv2.VideoWriter(str(new_video_path), cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                          (frame_width, frame_height))

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error opening video stream or file")

    count = 0
    while cap.isOpened():
        ret, frame = cap.read()  # Capture frame-by-frame
        if ret:
            out.write(frame)
            count += 1

            if count == final_video_size:
                break
            if final_video_size == 0:
                break
            if show:
                cv2.imshow('Frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def trim_video_with_eeg():
    """
    Method to trim videos from file. Video and xdf need to have the same name.
    :return:
    """
    datapath = Path("./data_raw")
    video_path = Path("./video")
    video_dst_path = Path("./video_trimmed")

    for f in datapath.glob("*.xdf"):
        file = f
        uid, session, trial, task = get_information(file) #If any problem check the regex functions.
        eeg_path = Path('./data_txt/') / "{:}_S{:02d}_T{:02d}_{:}_raw.txt".format(uid, session, trial, task)
        video_raw_path = video_path / (f.with_suffix("").name+"_left_color.avi")
        ts_raw_path =  video_path / (f.with_suffix("").name+"_left_color_ts.txt")
        new_video_path = video_dst_path / video_raw_path.name.replace("RE",str(session))
        new_ts_path = video_dst_path / ts_raw_path.name.replace("RE",str(session))
        print(video_raw_path)
        print(new_video_path)
        print(eeg_path)
        print(new_ts_path)

        trimVideoToSignals(new_video_path,new_ts_path,video_raw_path,ts_raw_path,eeg_path)

def iterateOverAllEegFiles():
    """
    Method to trim trials from a single big video
    :return:
    """
    root_path = Path(r"./")
    data_path = root_path / r"data_txt"

    video_path = root_path / r"video/video_right_color.avi"
    timestamps_path = root_path / r"video/video_right_color_ts.txt"

    for file in data_path.glob("*.txt"):
        uid = re.findall('.+(?=_S[0-9][0-9]+_T[0-9][0-9]_)', file.name)[0]
        session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9][0-9]_)', file.name)[0])
        trial = int(re.findall('(?<=_S[0-9]{2}_T)[0-9]{2}(?=_)', file.name)[0])
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.txt)', file.name)[0]

        if task == "Baseline":
            continue  # No video for baseline.
        else:
            print("Processing", uid, session, trial, task)
            new_video_name = "{:}_S{:02d}_T{:02d}_{:}_raw_video_right.avi".format(uid, int(session), int(trial), task)
            new_video_path = (root_path / "video") / new_video_name
            new_ts_name = "{:}_S{:02d}_T{:02d}_{:}_raw_video_right_ts.txt".format(uid, int(session), int(trial), task)
            new_ts_path = (root_path / "video") / new_ts_name
            trimVideoToSignals(new_video_path, new_ts_path, video_path, timestamps_path, file)


if __name__ == "__main__":
    #iterateOverAllEegFiles()
    trim_video_with_eeg()