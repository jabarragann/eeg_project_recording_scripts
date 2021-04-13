import mne
from pathlib import Path
import yasa
from scipy.signal import welch
import pandas as pd
import re
import numpy as np
from itertools import product
import matplotlib.pyplot as plt

from _ThesisRecordings.ScalpPlotUtils import create_scalp_plot
mne.set_log_level("WARNING")

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName

def calculate_features(eeg_epochs):
    eeg_epochs = eeg_epochs.get_data()  * 1e6

    # Calculate PSD
    sf = 250
    win = int(0.95 * sf)  # Window size is set to 4 seconds
    freqs, psd = welch(eeg_epochs, sf, nperseg=win, axis=-1)
    # psd  = 10 * np.log10(psd) #Change to dB

    # Calculate bandpower
    bands = [(4, 8, 'Theta'), (8, 12, 'Alpha'),(12,30,'Beta')]
    bands_names = ['Theta', 'Alpha','Beta']
    # Calculate the bandpower on 3-D PSD array
    bandpower = yasa.bandpower_from_psd_ndarray(psd, freqs, bands)
    # bandpower = bandpower.transpose([1, 2, 0])
    # bandpower = bandpower.mean(axis=1)
    # bandpower = pd.DataFrame(bandpower, columns=bands_names)

    #Experimental result
    columns = pd.MultiIndex.from_product([EEG_channels, bands_names], names=['ch', 'band'])
    bandpower_df = pd.DataFrame(index=range(eeg_epochs.shape[0]), columns= columns)
    idx = pd.IndexSlice

    for i, band in enumerate(bands):
        bandpower_df.loc[:,idx[:,band]] = bandpower[i,:,:]

    x=0

    return bandpower_df

#Dropped Fp1,Fp2,PO7,PO8,OZ
EEG_channels = list(map(renameChannels,["AF3","AF4","F7","F3","FZ","F4",
                                        "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                                        "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                                        "PZ","P4","P8","PO3","PO4"]))
parietal_ch = list(map(renameChannels,["P7","P3","PZ","P4","P8","PO4","PO3"]))
frontal_ch = list(map(renameChannels,["F7","F3","FZ","F4","F8","FC1","FC2"]))

def create_cognitive_full_features(data_path):
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
        # raw.crop(tmin=(raw.times[-1] - 120))

        # Create events every 20 seconds
        reject_criteria = dict(eeg=140e-6,)  # 100 µV
        events_array = mne.make_fixed_length_events(raw, start=0.5, stop=None, duration=0.5)
        epochs = mne.Epochs(raw, events_array, tmin=-0.5, tmax=0.5,reject=reject_criteria,preload=True)
        epochs.drop_bad()
        print(epochs.get_data().shape)
        # epochs.plot_drop_log(show=True, subject=uid)

        epochs = epochs.copy().pick(EEG_channels)

        bandpower_df = calculate_features(epochs)
        bandpower_df.loc[:, ('info','condition')] = task
        bandpower_df.loc[:, ('info', 'user')] = uid

        bandpower_df.to_csv(f.parent / 'eeg_features_full_set.csv')
        bandpower_df.to_pickle(f.parent / 'eeg_features_full_set.pd')

        # bandpower_df = bandpower_df.mean(axis=0)
        # create_scalp_plot(bandpower_df,v_min=0.150,v_max=0.5)
        # plt.show()

        # frontal_bandpower = calculate_features(frontal_epochs)
        # frontal_bandpower['area'] = 'frontal'
        # parietal_bandpower = calculate_features(parietal_epochs)
        # parietal_bandpower['area'] = 'parietal'
        #
        # final_feat = pd.concat((frontal_bandpower,parietal_bandpower))
        # final_feat['condition'] = task
        # final_feat['user'] = uid
        # final_feat.reset_index(drop=True)
        #
        # final_feat.to_csv(f.parent/'eeg_features.csv')

if __name__ == "__main__":

    path = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\01-JuanCollection2\2021-03-18_11h.46m.27s_juan-s2-manual01')
    create_cognitive_full_features(path)
