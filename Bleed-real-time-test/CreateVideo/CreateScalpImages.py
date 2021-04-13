import pickle
from mne.preprocessing import ICA
import numpy as np
import mne
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import cv2

##Software is removing last epoch of data
##Solution create events manually

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName

#Read eeg file
file = Path('./../lowTrial/U00_S1_T1_Low_pyprep.edf')
# file = Path('./../highTrial/U00_S1_T1_High_pyprep.edf')
raw = mne.io.read_raw_edf(file)

#Rename Channel
mne.rename_channels(raw.info, renameChannels)
#Set montage (3d electrode location)
raw = raw.set_montage('standard_1020')

# #####################################
# #New code ICA Blink removal analysis#
# #####################################
# raw.set_channel_types({'Fp1': 'eog'})
#
# filt_raw = raw.copy()
# filt_raw.load_data().filter(l_freq=1., h_freq=None)
#
# ica = ICA(n_components=20, random_state=97)
# ica.fit(filt_raw)
#
# ica.exclude = []
#
# # find which ICs match the ECG pattern
# eog_indices, eog_scores = ica.find_bads_eog(raw, )
# ica.exclude = eog_indices
#
# print("Excluding the following ICA components: ", eog_indices)
#
# reconst_raw = raw.copy().load_data()
# ica.apply(reconst_raw)

##Split data into epochs
#Create events every 20 seconds
events_array = mne.make_fixed_length_events(raw, start=1, stop=None, duration=2)
# events_array = np.vstack((events_array , [67500+5000,0,1]))

#Get 20 seconds Epochs from data
epochs = mne.Epochs(raw, events_array, tmin=-0.95, tmax=0.95, preload=True)
fig, axes = plt.subplots(1,4)
fig.patch.set_facecolor('grey')
# axes[0].set_facecolor('grey')

tsArray = np.zeros((events_array.shape[0]))
tsArray[:] = events_array[:,0]
scalpArray = np.zeros((len(epochs), 150, 600, 3))

for i in range(len(epochs)):
    print(i)
    #Select only first four epochs
    singleEpoch = epochs[i]
    singleEpoch.load_data()

    #Plot sensor location
    # singleEpoch.plot_sensors(kind='topomap', ch_type='all', show_names=True)

    #Frequency spatial distributions
    # bands_list = [(0, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 30, 'Beta'), (30, 45, 'Gamma')]
    bands_list = [(0.5, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 30, 'Beta') ]
    # bands_list = [ (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 30, 'Beta') ]
    epochFig = singleEpoch.plot_psd_topomap(bands=bands_list ,ch_type='eeg', normalize=True, show=False,\
                                             vlim=(0.0,0.5), cmap='RdBu_r')

    #Transform figure to image
    img = np.frombuffer(epochFig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(epochFig.canvas.get_width_height()[::-1] + (3,))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # img is rgb, convert to opencv's default bgr
    plt.close(epochFig)

    # scalpArray[i] = img
    print(img.shape)
    # display image with opencv or any operation you like
    cv2.imshow("plot", img)
    #
    #
    k = cv2.waitKey(0)



pickle.dump({'ts':tsArray,'img':scalpArray}, open(file.parent/"scalp.pickle","wb"))
cv2.destroyAllWindows()