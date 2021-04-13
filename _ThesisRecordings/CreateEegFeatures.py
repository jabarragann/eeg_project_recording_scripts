import mne
from pathlib import Path
import yasa
from scipy.signal import welch
import pandas as pd
import re
import numpy as np

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

    # psd  = 10 * np.log10(psd)
    # Calculate bandpower
    bands = [(4, 8, 'Theta'), (8, 12, 'Alpha')]
    bands_names = ['Theta', 'Alpha']
    # Calculate the bandpower on 3-D PSD array
    bandpower = yasa.bandpower_from_psd_ndarray(psd, freqs, bands)
    bandpower = bandpower.transpose([1, 2, 0])
    bandpower = bandpower.mean(axis=1)
    bandpower = pd.DataFrame(bandpower, columns=bands_names)

    return bandpower

#Dropped Fp1,Fp2,PO7,PO8,OZ
EEG_channels = list(map(renameChannels,["AF3","AF4","F7","F3","FZ","F4",
                                        "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                                        "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                                        "PZ","P4","P8","PO3","PO4"]))
parietal_ch = list(map(renameChannels,["P3", "P7", "PZ", "P4", "P8"]))
frontal_ch = list(map(renameChannels,["AF3", "AF4", "F3", "FZ"]))

def create_cognitive_reduce_features(data_path):
    preprocess = 'raw'
    for f in data_path.rglob("*{:}.edf".format(preprocess)):
        print(f.name)
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.edf)', f.name)[0]
        uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', f.name)[0]
        # Read eeg file
        raw = mne.io.read_raw_edf(f)

        # Rename Channel
        mne.rename_channels(raw.info, renameChannels)
        # Set montage (3d electrode location)
        raw = raw.set_montage('standard_1020')
        raw = raw.pick(EEG_channels)
        raw.crop(tmin=(raw.times[-1] - 120))

        # Create events every 20 seconds
        reject_criteria = dict(eeg=160e-6,)  # 100 µV
        events_array = mne.make_fixed_length_events(raw, start=0.5, stop=None, duration=0.5)
        epochs = mne.Epochs(raw, events_array, tmin=-0.5, tmax=0.5,reject=reject_criteria,preload=True)
        epochs.drop_bad()
        print(epochs.get_data().shape)
        # epochs.plot_drop_log(show=True, subject=uid)

        frontal_epochs = epochs.copy().pick(frontal_ch)
        parietal_epochs = epochs.copy().pick(parietal_ch)

        frontal_bandpower = calculate_features(frontal_epochs)
        frontal_bandpower['area'] = 'frontal'
        parietal_bandpower = calculate_features(parietal_epochs)
        parietal_bandpower['area'] = 'parietal'

        final_feat = pd.concat((frontal_bandpower,parietal_bandpower))
        final_feat['condition'] = task
        final_feat['user'] = uid
        final_feat.reset_index(drop=True)

        final_feat.to_csv(f.parent/'eeg_features.csv')

        ratio = pd.DataFrame (frontal_bandpower['Theta'] / parietal_bandpower['Alpha'], columns=['ratio'])
        ratio['condition'] = task
        ratio['user'] = uid
        ratio.to_csv(f.parent/'thetaf-alphap.csv')


if __name__ == "__main__":

    path = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\01-JuanCollection2\2021-03-18_11h.46m.27s_juan-s2-manual01')
    create_cognitive_reduce_features(path)
