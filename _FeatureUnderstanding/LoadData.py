import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import yasa
import mne
import re
import pandas as pd
from itertools import product
from pathlib import Path

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')

    return chName

#PO7 and PO8 and Oz removed
EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO3","PO4","OZ"]
Power_coefficients = ['Delta','Theta','Alpha','Beta']
renamedChannels = list(map(renameChannels,EEG_channels))
newColumnNames = [x+'-'+y for x,y in product(Power_coefficients,renamedChannels)]


def splitDataIntoEpochs(raw, frameDuration, overlap):
    # Split data into epochs
    w1 = frameDuration
    sf = 250
    totalPoints = raw.get_data().shape[1]
    nperE = sf * w1  # Number of samples per Epoch

    eTime = int(w1 / 2 * sf) + raw.first_samp
    events_array = []
    while eTime < raw.last_samp:
        events_array.append([eTime, 0, 1])
        eTime += sf * (w1 - overlap)

    events_array = np.array(events_array).astype(np.int)
    epochs = mne.Epochs(raw, events_array, tmin=-(w1 / 2), tmax=(w1 / 2))

    return epochs

def getBandPowerCoefficients(epoch_data):
    counter = 0
    dataDict = {}
    epoch_data.load_data()
    win_sec =0.95
    sf = 250

    for i in range(len(epoch_data)):
        data = epoch_data[i]
        data = data.get_data().squeeze() #Remove additional
        data *= 1e6

        #Check that data is in the correct range
        assert all([1 < abs(data[4, :].min()) < 800,
                    1 < abs(data[7, :].max()) < 800,
                    1 < abs(data[15, :].min()) < 800]), \
                    "Check the units of the data that is about to be process. " \
                    "Data should be given as uv to the get bandpower coefficients function "

        # Calculate bandpower # Data should always be process in the uv
        bd = yasa.bandpower(data, sf=sf, ch_names=EEG_channels, win_sec=win_sec,
                            bands=[(4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 40, 'Beta')])
        # Reshape coefficients into a single row vector with the format
        # [Fp1Theta,Fp2Theta,AF3Theta,.....,Fp1Alpha,Fp2Alpha,AF3Alpha,.....,Fp1Beta,Fp2Beta,AF3Beta,.....,]
        bandpower = bd[Power_coefficients].transpose()
        bandpower = bandpower.values.reshape(1, -1)
        # Create row name, label and add to data dict
        rowName = 'T' + str(i) + '_' + str(counter)
        dataDict[rowName] = np.squeeze(bandpower)
        # Update counter
        counter += 1

    powerBandDataset = pd.DataFrame.from_dict(dataDict, orient='index', columns=newColumnNames)

    return powerBandDataset

def loadSingleTxtFile(filePathLib,frameDuration, overlap, labels=None):

    X = None
    y = None

    uid = re.findall('.+(?=_S[0-9]{2}_T[0-9]{2}_)', filePathLib.name)[0]
    session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]{2}_)', filePathLib.name)[0])
    trial = int(re.findall('(?<=_S[0-9]{2}_T)[0-9]{2}(?=_)', filePathLib.name)[0])
    task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.txt)', filePathLib.name)[0]
    print("file information:", uid, session, trial, task)

    #Get Label
    label = None
    if task == labels[0]:
        label = 0.0
    elif task == labels[1]:
        label = 1.0
    assert task == labels[0] or task == labels[1], "something went wrong with the labels. check {:}".format(filePathLib.name)
    # Read eeg file
    eeg_file = pd.read_csv(filePathLib)
    data = eeg_file[EEG_channels].values.transpose()
    data = data
    ch_names = EEG_channels
    ch_types = ["eeg"] * len(ch_names)
    info = mne.create_info(ch_names=ch_names, sfreq=250, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)

    mne.rename_channels(raw.info, renameChannels)
    raw = raw.pick(renamedChannels)  #Remove bad channels
    # Filter data
    raw.load_data()
    raw.filter(0.5, 30)

    #Get epochs
    epochs = splitDataIntoEpochs(raw,frameDuration,overlap)
    bandpower = getBandPowerCoefficients(epochs)

    images = bandpower.values

    # Append all the samples in a list
    if X is None:
        X = images
        y = np.ones(len(images)) * label
    else:
        X = np.concatenate((X, images), axis=0)
        y = np.concatenate((y, np.ones(len(images)) * label), axis=0)

    return X, np.array(y)


def main():
    p = Path(r"C:\Users\asus\OneDrive - purdue.edu\RealtimeProject\Experiments3-Data\CalibrationProcedure-NeedlePasssingBlood\edf\Jing\UJing_S01_T01_NeedlePassing_raw.edf")
    X, y = loadSingleTxtFile(p,frameDuration=5,overlap=2.5,labels=['NeedlePassing','BloodNeedle'])

if __name__ == "__main__":
    main()