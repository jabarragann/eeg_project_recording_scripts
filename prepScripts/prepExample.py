# First we import what we need for this example.


import os
import pathlib
import mne
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

from pyprep.prep_pipeline import PrepPipeline


def chn_name_mapping(ch_name):
    """Map channel names to fit standard naming convention."""
    ch_name = ch_name.strip('.')
    ch_name = ch_name.upper()
    if 'Z' in ch_name:
        ch_name = ch_name.replace('Z', 'z')

    if 'FP' in ch_name:
        ch_name = ch_name.replace('FP', 'Fp')

    return ch_name

###############################################################################
# General settings and file paths
mne.set_log_level("WARNING")
here = pathlib.Path("__file__").parent.absolute()

# Raw data
fname_test_file = os.path.join(here, 'data', 'S004R01.edf')

###############################################################################
# Load data and prepare it
# ------------------------

raw = mne.io.read_raw_edf(fname_test_file, preload=True)
# Rename channels to fit with standard conventions
raw.rename_channels(chn_name_mapping)
# Add a montage to the data
montage_kind = "standard_1005"
montage = mne.channels.make_standard_montage(montage_kind)

# Extract some info
eeg_index = mne.pick_types(raw.info, eeg=True, eog=False, meg=False)
ch_names = raw.info["ch_names"]
ch_names_eeg = list(np.asarray(ch_names)[eeg_index])
sample_rate = raw.info["sfreq"]

# Make a copy of the data
raw_copy = raw.copy()

#Filter data
ch = np.arange(0,3)
filtered = raw.filter(0.5,30)

scalings = {'eeg': 0.00005}  # Could also pass a dictionary with some value == 'auto'
plot1 = filtered.plot(n_channels=32, scalings=scalings, title='Original',
         show=False, block=False)

raw_copy = filtered.copy()
# Fit prep
prep_params = {'ref_chs': ch_names_eeg,
               'reref_chs': ch_names_eeg,
               'line_freqs': np.arange(60, sample_rate/2, 60)}
prep = PrepPipeline(raw_copy, prep_params, montage)
prep.fit()


final_eeg = prep.raw

plot2 = final_eeg.plot(n_channels=32, scalings=scalings, title='Pyprep',
         show=False, block=False)

plt.show()

