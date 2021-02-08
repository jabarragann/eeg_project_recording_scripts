import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import mne
import yasa

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO3","PO4","OZ"]

bands  = ['Delta','Theta','Alpha', 'Beta']
titles = ["Delta [0.5-4Hz]","Theta [4-8Hz]","Alpha [8-12Hz]","Beta [12-30Hz]"]

def plot_workload_idx(dataDict,eventToShow, ax):
    pred, time = dataDict['pred']['data'], dataDict['pred']['time']
    alarm, alarmTime = dataDict['alarm']['data'], dataDict['alarm']['time']

    ax.plot(time, pred)

    # Plot alarm events
    color_dict = {'low workload': 'blue', 'medium workload': 'green', 'high workload': 'red'}
    label_dict = {'low workload': 'low', 'medium workload': 'medium', 'high workload': 'high'}

    #Show only selected event, one before and one after
    for idx in range(-1,2):
        c = color_dict[alarm[eventToShow+idx, 0]]
        l = label_dict[alarm[eventToShow+idx, 0]]
        ax.axvline(x=alarmTime[eventToShow+idx], color=c, linestyle='--', label=l)

    ax.set_ylabel('workload index')
    ax.set_xlabel('time(s)')

    # Create custom artists
    HighArtist = plt.Line2D((0, 1), (0, 0), color='r')
    MediumArtist = plt.Line2D((0, 1), (0, 0), color='g')
    LowArtist = plt.Line2D((0, 1), (0, 0), color='b')

    # Create legend from custom artist/label lists
    ax.legend([HighArtist, MediumArtist, LowArtist], ['High', 'Medium', 'Low'])
    ax.grid()
    return ax


def create_topo(data, fig_title, ax, v_min=-0.022, v_max=0.022):
    from mne.viz import plot_topomap

    mask = np.array([True for ch in EEG_channels])

    locations = pd.read_csv('./channel_2d_location.csv', index_col=0)
    locations = locations.drop(index=["PO8", "PO7"])

    mask_params = dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                       linewidth=0, markersize=10)

    print("{:} Data max {:0.3f} Data min {:0.3f}".format(fig_title, data.max(), data.min()))

    im, cn = plot_topomap(data.values, locations[['x', 'y']].values,
                          outlines='head', axes=ax, cmap='jet', show=False,
                          names=EEG_channels, show_names=True,
                          mask=mask, mask_params=mask_params,
                          vmin=v_min, vmax=v_max, contours=7)
    ax.set_title(fig_title, fontsize=10)
    return im

def clean_axes(a):
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.spines["left"].set_visible(False)
    a.spines["bottom"].set_visible(False)
    a.set_xticks([])
    a.set_xticks([],minor=True)
    a.set_yticks([])
    a.set_yticks([],minor=True)

def create_scalp_plot(data, v_min=-0.5, v_max=0.5):
    fig, axes = plt.subplots(1, 5, figsize=(15, 5), gridspec_kw={'width_ratios': [3, 3, 3, 3, 1]})
    axes = axes.reshape((-1, 1)).squeeze()

    for b,t,ax in zip(bands, titles,axes):
        im = create_topo(data[b], t, ax, v_min=v_min, v_max=v_max)

    cbar = fig.colorbar(im, ax=axes[-1])
    clean_axes(axes[-1])

    ti = 'dB change from low state'
    cbar.ax.set_ylabel(ti, rotation=270, fontsize=10, labelpad=15)
    cbar.ax.yaxis.set_ticks_position('left')

    fig.tight_layout()

def obtain_spectral_features(data, win=4.0,sf=250):
    win_sec = win
    data = data.squeeze() * 1e6 #Go back to volts
    bandpower = yasa.bandpower(data,
                       sf=sf, ch_names=EEG_channels, win_sec=win_sec,
                       bands=[(0.5, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'),
                              (12, 30, 'Beta'), (30, 50, 'Gamma')])
    return bandpower[bands]

def main():
    dataPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments4-Data\01-Juan-Feedback-experiment")
    trial = 12
    fileRootName = "Ujuan_S01_T{:2d}_BloodDynamic".format(trial)
    dataPath = dataPath / fileRootName
    eventToExtract =2 #,13 8,2 #Greater than 0

    #load data
    eegData = pd.read_csv(dataPath / (fileRootName + "_raw.txt"))
    #Load events
    eventsData = pickle.load(open(dataPath/(fileRootName + "_raw_intervention.pickle"),'rb' ))
    alarm, alarmTime = eventsData['alarm']['data'], eventsData['alarm']['time']

    #Obtain data from event
    eegData = eegData.loc[(eegData['LSL_TIME']>alarmTime[eventToExtract-1]) &
                          (eegData['LSL_TIME']<alarmTime[eventToExtract+1])]
    eegData = eegData[EEG_channels].values.transpose()
    eegData = eegData / 1e6 # Convert from uv to v
    ch_names = EEG_channels
    ch_types = ["eeg"] * len(ch_names)
    info = mne.create_info(ch_names=ch_names, sfreq=250, ch_types=ch_types)
    raw = mne.io.RawArray(eegData, info)

    #create epochs
    new_events = np.zeros((2,3)).astype(np.int32)
    new_events[:,0] = list(map(int,[5*250, 15*250])); new_events[:,2] = [1,1]
    epochs = mne.Epochs(raw, new_events, tmin=-5, tmax=5)

    #Create features
    beforeStimulusFeat = obtain_spectral_features(epochs[0].get_data(),win=2.0)
    afterStimulusFeat = obtain_spectral_features(epochs[1].get_data(), win=2.0)
    bandpower = 10*np.log10(afterStimulusFeat/beforeStimulusFeat)  #Differences in decibels

    #Plot events
    fig, axes = plt.subplots(1,1)

    plot_workload_idx(eventsData,eventToExtract, axes)
    create_scalp_plot(bandpower,v_min=-8.0,v_max=8.0)

    plt.show()


if __name__ == "__main__":
    main()