import numpy as np
import mne
import pandas as pd
from pathlib import Path

file = Path('./data-processed/Santy_S001_T002_Normal.txt')
# file = Path('./data-processed/Santy_S001_T003_Inv.txt')

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO3","PO4","OZ"]
# EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
#                 "F8","FC5","FC1","FC2","FC6","CZ","PZ","OZ"]
sfreq = 250

df = pd.read_csv(file)
data = df[EEG_channels].values.transpose()
ch_names = EEG_channels
ch_types = ["eeg"] * len(ch_names)

# It is also possibl e to use info from another raw object.
info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
raw = mne.io.RawArray(data, info)

scalings = {'eeg': 10}  # Could also pass a dictionary with some value == 'auto'
raw.plot(n_channels=32, scalings=scalings, title='Auto-scaled Data from arrays',
         show=True, block=True)