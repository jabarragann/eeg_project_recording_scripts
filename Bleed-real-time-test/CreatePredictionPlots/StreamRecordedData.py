import time
import numpy as np
import mne
from pylsl import StreamInfo, StreamOutlet
from pathlib import Path

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName


# next make an outlet
EEG_channels = [  "FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                  "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                  "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                  "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]

Power_coefficients = ['Delta', 'Theta', 'Alpha', 'Beta']

info = StreamInfo('Gnautilus', 'EEG',30, 250, 'float32', 'myuid34234')
outlet = StreamOutlet(info)

if __name__ == '__main__':

    # Read eeg file
    srcPath =  Path('./../lowTrial').resolve()
    file = srcPath / "U00_S1_T1_low_pyprep.edf"

    # srcPath =  Path('./../highTrial').resolve()
    # file = srcPath / "U00_S1_T1_High_pyprep.edf"

    raw = mne.io.read_raw_edf(file, preload=True)
    raw.drop_channels(['PO7','PO8'])
    # raw = raw.pick(EEG_channels)
    rawArray = raw.get_data(picks=['eeg'])
    events_array = mne.make_fixed_length_events(raw, start=1, stop=None, duration=2)

    print("Sending data ...")
    for idx in range(rawArray.shape[1]):
        # now send it and wait for a bit
        outlet.push_sample(rawArray[:,idx])
        time.sleep(0.004/4)

    print("Finished sending data")