import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import pickle

#Paths
# dataPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments4-Data\01-Juan-Feedback-experiment")
# trial = 6
# fileRootName = "Ujuan_S01_T{:02d}_Assistant".format(trial) #BloodDynamic
# path = dataPath / fileRootName / (fileRootName + "_raw_intervention.pickle")
#
dataPath = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments4-Data\02-Jing-Feedback-experiment")
trial = 4
fileRootName = "Ujing_S01_T{:02d}_DynamicBlood".format(trial)
path = dataPath / (fileRootName + "_raw_intervention.pickle")

def main():
    # path = Path('./prediction_events') / r'Ujuan_S01_T12_BloodDynamic_raw_intervention.pickle'
    dataDict = pickle.load(open(path, 'rb'))
    x=0

    pred,time = dataDict['pred']['data'], dataDict['pred']['time']
    if pred is None:
        pred,time=[],[]

    alarm, alarmTime = dataDict['alarm']['data'], dataDict['alarm']['time']

    fig, ax = plt.subplots(1,1, figsize=(7,4))
    ax.plot(time, pred)

    #Plot alarm events
    color_dict = {'low workload':'blue','medium workload':'green','high workload':'red'}
    label_dict = {'low workload': 'low', 'medium workload': 'medium', 'high workload': 'high'}
    for idx in range(alarm.shape[0]):
        c = color_dict[alarm[idx,0]]
        l = label_dict[alarm[idx,0]]
        # plt.axvline(x=alarmTime[idx], color=c, linestyle='--', label=l)

    ax.set_ylabel('workload index')
    ax.set_xlabel('time(s)')

    # Create custom artists
    HighArtist = plt.Line2D((0, 1), (0, 0), color='r')
    MediumArtist = plt.Line2D((0, 1), (0, 0), color='g')
    LowArtist =  plt.Line2D((0, 1), (0, 0), color='b')

    # Create legend from custom artist/label lists
    ax.legend([HighArtist, MediumArtist, LowArtist], ['High','Medium','Low'])
    plt.grid()
    plt.show()


if __name__ == "__main__":
	main()