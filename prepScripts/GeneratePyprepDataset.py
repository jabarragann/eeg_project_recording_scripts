from pathlib import Path
import pandas as pd
import mne
import numpy as np
from pyprep.prep_pipeline import PrepPipeline
import matplotlib.pyplot as plt

def chn_name_mapping(ch_name):
    """Map channel names to fit standard naming convention."""
    ch_name = ch_name.strip('.')
    ch_name = ch_name.upper()
    if 'Z' in ch_name:
        ch_name = ch_name.replace('Z', 'z')

    if 'FP' in ch_name:
        ch_name = ch_name.replace('FP', 'Fp')

    return ch_name

EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]

# General settings and file paths
mne.set_log_level("WARNING")

if __name__ == "__main__":

    # srcPath = "C:/Users/asus/OneDrive - purdue.edu/RealtimeProject/Data/G.NautilusInvertedTask_Formatted"
    # dstPath = "C:/Users/asus/OneDrive - purdue.edu/RealtimeProject/Data/GNautilusInvertedTask_Pyprep"

    srcPath = "C:/Users/asus/PycharmProjects/EEG-recording-lsl/data-processed"
    dstPath = "C:/Users/asus/PycharmProjects/EEG-recording-lsl/prepScripts/pyprepResult"

    summaryFile = open("./summary.txt",'w')

    src = Path(srcPath)
    dst = Path(dstPath)

    for file in src.rglob("*.txt"):
        print("Processsing ",file.name)

        p2 = dst / file.parent.name
        if not p2.exists():
            p2.mkdir(parents=True)

        sfreq = 250

        df = pd.read_csv(file)
        data = df[EEG_channels].values.transpose()

        # Convert from uv to v
        data = data / 1e6
        ch_names = EEG_channels
        ch_types = ["eeg"] * len(ch_names)
        # It is also possible to use info from another raw object.
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        raw = mne.io.RawArray(data, info)

        # raw = raw.crop(0, 15).load_data()

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

        # Fit prep
        prep_params = {'ref_chs': ch_names_eeg,
                       'reref_chs': ch_names_eeg,
                       'line_freqs': np.arange(60, sample_rate / 2, 60)}
        prep = PrepPipeline(raw_copy, prep_params, montage)
        prep.fit()

        final_eeg = prep.raw


        #Write pyprep summary of interpolation
        summaryFile.write(file.name + "\n")
        summaryFile.write(str(prep.interpolated_channels)+"\n")
        summaryFile.flush()

        #Write new data
        eegData = final_eeg.get_data().transpose() *  1e6
        finalFrame = pd.DataFrame(data=eegData, index=None, columns=EEG_channels)
        finalFrame["COMPUTER_TIME"] = df["COMPUTER_TIME"]
        finalFrame["label"] = df["label"]

        newName = dst / file.parent.name / (file.with_suffix('').name +'_pyprep.txt')
        finalFrame.to_csv(newName, index=None)

        # scalings = {'eeg': 0.00005}
        # plot2 = final_eeg.plot(n_channels=32, scalings=scalings, title=newName.name,
        #                        show=False, block=False)
        # plt.show()

