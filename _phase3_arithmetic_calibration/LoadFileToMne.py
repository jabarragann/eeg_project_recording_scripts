import numpy as np
import mne
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName

file = Path('./data_edf/UJing_S02_T01_Baseline_raw.edf')

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]
sfreq = 250

#Read eeg data
raw = mne.io.read_raw_edf(file)

#Rename Channel
mne.rename_channels(raw.info, renameChannels)
#Set montage (3d electrode location)
raw = raw.set_montage('standard_1020')

# filtered = raw.filter(0.5,30)

scalings = {'eeg': 0.00003}  # Could also pass a dictionary with some value == 'auto'

raw.plot(n_channels=32, scalings=scalings, title='Auto-scaled Data from arrays',
         show=True, block=True)