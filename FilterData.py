import numpy as np
import mne
import pandas as pd
from pathlib import Path

# file = Path('./data-processed/juan_S3_T5_epoc.txt')
# file = Path('./data-processed/Karuna_S3_T1_Normal.txt')
file = Path('./data-processed/Karuna_S3_T2_Inv.txt')

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]

dataPath = Path("./data-processed")

for file in dataPath.glob("*.txt"):
    print(file.name)
    sfreq = 250

    df = pd.read_csv(file)
    data = df[EEG_channels].values.transpose()

    #Convert from uv to v
    data = data
    ch_names = EEG_channels
    ch_types = ["eeg"] * len(ch_names)

    # It is also possible to use info from another raw object.
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)

    filtered = raw.filter(0.5,30)

    eegData = filtered.get_data().transpose()
    finalFrame =  pd.DataFrame(data=eegData, index=None, columns=EEG_channels)
    finalFrame["COMPUTER_TIME"] = df["COMPUTER_TIME"]
    finalFrame["label"] = df["label"]


    finalFrame.to_csv('./data-filtered/' + file.name, index = None)

    # scalings = {'eeg': 10}  # Could also pass a dictionary with some value == 'auto'
    # filtered.plot(n_channels=32, scalings=scalings, title='Auto-scaled Data from arrays',
    #          show=True, block=True)