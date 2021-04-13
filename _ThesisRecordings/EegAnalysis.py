import mne
from pathlib import Path
import yasa
from scipy.signal import welch
import pandas as pd
import re
mne.set_log_level("WARNING")

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName

def calculate_features(eeg_epochs):
    eeg_epochs = eeg_epochs.get_data()

    # Calculate PSD
    sf = 250
    win = int(0.95 * sf)  # Window size is set to 4 seconds
    freqs, psd = welch(eeg_epochs, sf, nperseg=win, axis=-1)

    # Calculate bandpower
    bands = [(4, 8, 'Theta'), (8, 12, 'Alpha')]
    bands_names = ['Theta', 'Alpha']
    # Calculate the bandpower on 3-D PSD array
    bandpower = yasa.bandpower_from_psd_ndarray(psd, freqs, bands)
    bandpower = bandpower.transpose([1, 2, 0])
    bandpower = bandpower.mean(axis=1)
    bandpower = pd.DataFrame(bandpower, columns=bands_names)

    return bandpower

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]
parietal_ch = list(map(renameChannels,["P7","P3","PZ","P4","P8","PO4","PO3"]))
frontal_ch = list(map(renameChannels,["F7","F3","FZ","F4","F8","FC1","FC2"]))

if __name__ == "__main__":

    path_list = [Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\06-KeyuCollection\2021-03-14_12h.31m.16s_keyu-autonomy-02'),
                 Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\06-KeyuCollection\2021-03-14_12h.24m.47s_keyu-manual-02'),
                 ]
    data_path = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\02-AlfredoCollection1')

    for f in data_path.rglob("*.edf"):
        print(f.name)
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.edf)', f.name)[0]
        uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', f.name)[0]