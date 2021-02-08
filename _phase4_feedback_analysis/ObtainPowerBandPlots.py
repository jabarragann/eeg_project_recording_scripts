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

bands  = ['Delta','Theta','Alpha','Beta']
titles = ["Delta [0.5-4Hz]","Theta [4-8Hz]","Alpha [8-12Hz]","Beta [12-30Hz]"]

# ch_cluster1 = ['F8','F4','FC6']
ch_cluster1 = EEG_channels

def splitDataIntoEpochs(raw, frameDuration, overlap):
    w1 = frameDuration
    sf = 250

    eTime = int(w1 / 2 * sf) + raw.first_samp
    events_array = []
    while eTime < raw.last_samp:
        events_array.append([eTime, 0, 1])
        eTime += sf * (w1 - overlap)

    events_array = np.array(events_array).astype(np.int)
    epochs = mne.Epochs(raw, events_array, tmin=-(w1 / 2), tmax=(w1 / 2))

    return epochs

def plot_event(dataDict,eventToShow, ax):
    alarm, alarmTime = dataDict['alarm']['data'], dataDict['alarm']['time']

    # Plot alarm events
    color_dict = {'low workload': 'blue', 'medium workload': 'green', 'high workload': 'red'}
    label_dict = {'low workload': 'low', 'medium workload': 'medium', 'high workload': 'high'}

    # Show only selected event, one before and one after
    for idx in range(-1, 2):
        c = color_dict[alarm[eventToShow + idx, 0]]
        l = label_dict[alarm[eventToShow + idx, 0]]
        ax.axvline(x=alarmTime[eventToShow + idx], color=c, linestyle='--')
    return ax

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


    # Create custom artists
    HighArtist = plt.Line2D((0, 1), (0, 0), color='r')
    MediumArtist = plt.Line2D((0, 1), (0, 0), color='g')
    LowArtist = plt.Line2D((0, 1), (0, 0), color='b')

    # Create legend from custom artist/label lists
    ax.legend([HighArtist, MediumArtist, LowArtist], ['High', 'Medium', 'Low'],
              loc=(1.02, 0), fontsize='xx-small')
    ax.grid()
    return ax

def obtain_spectral_features_from_epochs(epochs, win=4.0,sf=250):
    results = pd.DataFrame(columns=bands)
    cluster = ch_cluster1
    for idx, e in enumerate(epochs):
        feat = obtain_spectral_features(e)
        feat = feat.loc[cluster].mean()
        ts = epochs[idx].events[0][0]/250
        results.loc[ts,:] = feat

    return results

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
    eegData = eegData[EEG_channels].values.transpose()
    eegData = eegData / 1e6 # Convert from uv to v
    ch_names = EEG_channels
    ch_types = ["eeg"] * len(ch_names)
    info = mne.create_info(ch_names=ch_names, sfreq=250, ch_types=ch_types)
    raw = mne.io.RawArray(eegData, info)

    #create epochs
    epochs = splitDataIntoEpochs(raw,8,2)

    #Create features
    results = obtain_spectral_features_from_epochs(epochs, win=1.4)

    #Plot events
    fig, axes = plt.subplots(5,1, sharex=True)
    fig_params = dict(top = 0.922, bottom = 0.112, left = 0.1, right = 0.781, hspace = 0.2, wspace = 0.2)
    plt.subplots_adjust(**fig_params)

    axes = axes.reshape(-1)
    plot_workload_idx(eventsData,eventToExtract, axes[0])


    for b,ax in zip(bands,axes[1:]):
        ax.plot(results[b],label=b)
        moving_avg = results[b].rolling(10).mean().fillna(value=0)
        ax.plot(moving_avg,label= b +" avg 10")
        ax.grid()
        ax.set_ylim([0,results[b].max()])
        ax.legend(loc=(1.02, 0), fontsize='xx-small')
        plot_event(eventsData,eventToExtract,ax)

    ax.set_xlabel('time(s)')
    plt.show()


if __name__ == "__main__":
    main()