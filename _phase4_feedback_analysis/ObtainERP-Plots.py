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

ch_cluster1 = ['F7','F3','F8','F4','FZ']
# ch_cluster1 = EEG_channels

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
    for idx in range(len(alarmTime)):
    # for idx in range(-1, 2):
        c = color_dict[alarm[idx, 0]]
        l = label_dict[alarm[idx, 0]]
        ax.axvline(x=alarmTime[idx], color=c, linestyle='--')
    return ax

def plot_workload_idx(dataDict,eventToShow, ax):
    pred, time = dataDict['pred']['data'], dataDict['pred']['time']
    alarm, alarmTime = dataDict['alarm']['data'], dataDict['alarm']['time']

    if pred is None:
        pred,time=[],[]

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
              loc=(1.02, 0.5), fontsize='xx-small')
    ax.grid()
    return ax

def obtain_spectral_features_from_epochs(epochs, win =None):
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
    dataPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments4-Data\01-juan-Feedback-experiment")
    user = 'juan'
    trial = [6]
    task = "Assistance"
    # fileRootName = "U{:}_S01_T{:02d}_{:}".format(user, trial, task)  # BloodDynamic
    # dataPath = dataPath / fileRootName
    #

    # dataPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments4-Data\03-Keyu-Feedback-experiment")
    # user = 'keyu'
    # trial = [1,3]
    # task = "Microbreak"

    listOfSegments = []
    for t in trial:
        fileRootName = "U{:}_S01_T{:02d}_{:}".format(user,t,task) #BloodDynamic
        dataPath = dataPath / fileRootName
        eventToExtract = 3 #,13 8,2 #Greater than 0

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
        epochs = splitDataIntoEpochs(raw,2,1)

        #Create features
        results = obtain_spectral_features_from_epochs(epochs, win=1.4)


        w1 = 7
        for idx , a in enumerate(alarmTime):
            if alarm[idx,0] == "high workload":
                segment = results.loc[(results.index > a-w1) & (results.index < a+w1)]
                listOfSegments.append([a,segment])


    # Calculate average ERP
    averageFrame = None
    times = None
    for a,segment in listOfSegments:
        if averageFrame is None:
            averageFrame = segment.reset_index()
            times = averageFrame['index'] - a
        else:
            if segment.reset_index().shape == averageFrame.shape:
                averageFrame = averageFrame + segment.reset_index()
    averageFrame /= len(listOfSegments)

    #Plot events
    fig, axes = plt.subplots(4,1)
    fig_params = dict(top = 0.922, bottom = 0.112, left = 0.140, right = 0.85, hspace = 0.45, wspace = 0.2)
    plt.subplots_adjust(**fig_params)

    axes = axes.reshape(-1)

    axes[0].set_title("Average ERP for powerbands. Feedback={:} N={:d}".format(task, len(listOfSegments)))
    for b, ax in zip(bands,axes):
        db_bands = 10*np.log10(averageFrame[b].values.astype(np.float))
        ax.plot(times.values,db_bands, label="avg " + b)
        ax.axvline(0)
        ax.legend(loc=(1.02, 0.5), fontsize='xx-small')
        ax.grid()
        ax.set_ylabel('dB')
    plt.show()


if __name__ == "__main__":
    main()