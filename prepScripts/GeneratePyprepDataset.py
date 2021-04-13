import re
from pathlib import Path
import pandas as pd
import mne
import numpy as np
from pyprep.prep_pipeline import PrepPipeline
import matplotlib.pyplot as plt
from pyedflib import highlevel
import pyedflib

#Global variables
EEG_channels = ["FP1","FP2","AF3","AF4","F7","F3","FZ","F4",
                "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                "PZ","P4","P8","PO7","PO3","PO4","PO8","OZ"]
# General settings and file paths
mne.set_log_level("WARNING")

def chn_name_mapping(ch_name):
    """Map channel names to fit standard naming convention."""
    ch_name = ch_name.strip('.')
    ch_name = ch_name.upper()
    if 'Z' in ch_name:
        ch_name = ch_name.replace('Z', 'z')

    if 'FP' in ch_name:
        ch_name = ch_name.replace('FP', 'Fp')

    return ch_name

def get_file_info(file):
    # Rename files --> remove identifiers
    status = True
    try:
        uid = re.findall('.+(?=_S[0-9]{2}_T[0-9]{2}_)', file.name)[0]
        session = re.findall('(?<=_S)[0-9]{2}(?=_T[0-9]{2}_)', file.name)[0]
        trial = re.findall('(?<=_S[0-9]{2}_T)[0-9]{2}(?=_)', file.name)[0]
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_)', file.name)[0]
        preprocess = re.findall('(?<=_{:}_).+(?=\.txt)'.format(task), file.name)[0]
    except:
        status = False
        return status,None,None,None,None,None,
    return status, uid,session,trial,task,preprocess

def load_to_mne (file):
    #Sampling freq
    sfreq = 250
    #Read txt file
    df = pd.read_csv(file)
    data = df[EEG_channels].values.transpose()
    # Convert from uv to v
    data = data / 1e6
    #Create raw object
    ch_names = EEG_channels
    ch_types = ["eeg"] * len(ch_names)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)

    # Rename channels to fit with standard conventions
    raw.rename_channels(chn_name_mapping)
    # Add a montage to the data
    montage_kind = "standard_1005"
    montage = mne.channels.make_standard_montage(montage_kind)

    return raw, montage


def write_data_edf(raw, dst_file, uid, task):
    sfreq = 250
    data = raw.get_data() * 1e6

    # Create writer
    writer = pyedflib.EdfWriter(str(dst_file), len(EEG_channels), file_type=1)

    # Create header
    writer.setPatientName(uid)

    # assert task == 'pegNormal' or 'pegInversion'
    # if task == 'pegNormal' or 'Low':
    #     label = 'low workload'
    # elif task == 'pegInversion' or 'High':
    #     label = 'high workload'
    # writer.setPatientAdditional(label)

    # Signals
    signal_headers = highlevel.make_signal_headers(EEG_channels, sample_rate= sfreq)
    writer.setSignalHeaders(signal_headers)
    writer.writeSamples(data)

    # close
    writer.close()


def use_pyprep(srcPath, dstPath):
    summaryFile = open("./summary.txt", 'a')

    src = Path(srcPath)
    dst = Path(dstPath)

    session_list = [1, 4]
    for file in src.glob("*.txt"):

        status, uid, session, trial, task, preprocess = get_file_info(file)
        # print(file)
        if status:
            x = 0
            # if task != 'Baseline' and int(session) in session_list:
            dst_file = dst / (file.with_suffix('').name[:-3] + 'pyprep.edf')
            print("Processsing ", file.name)

            raw, montage = load_to_mne(file)

            # # #Only for debugging purposes
            # raw = raw.crop(0, 15).load_data()

            raw.crop(tmin=(raw.times[-1] - 120)) #Get only last two minutes

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

            # Write pyprep summary of interpolation
            summaryFile.write(file.name + "\n")
            summaryFile.write(str(prep.interpolated_channels) + "\n")
            summaryFile.flush()

            write_data_edf(final_eeg, dst_file, uid, task)

            # #Plot signal, debugging
            # scalings = {'eeg': 0.00005}
            # plot2 = final_eeg.plot(n_channels=32, scalings=scalings, title=dst_file.name,
            #                        show=False, block=False)
            # plt.show()

            # #Write new data -- .txt
            # eegData = final_eeg.get_data().transpose() *  1e6
            # finalFrame = pd.DataFrame(data=eegData, index=None, columns=EEG_channels)
            # finalFrame["COMPUTER_TIME"] = df["COMPUTER_TIME"]
            # finalFrame["label"] = df["label"]
            #
            # newName = dst / file.parent.name / (file.with_suffix('').name +'_pyprep.txt')
            # finalFrame.to_csv(newName, index=None)
            #
            # break

def main():
    # srcPath = "C:/Users/asus/OneDrive - purdue.edu/RealtimeProject/Data/G.NautilusInvertedTask_Formatted"
    # dstPath = "C:/Users/asus/OneDrive - purdue.edu/RealtimeProject/Data/GNautilusInvertedTask_Pyprep"
    # srcPath = "C:/Users/asus/PycharmProjects/EEG-recording-lsl/data-processed"
    # dstPath = "C:/Users/asus/PycharmProjects/EEG-recording-lsl/prepScripts/pyprepResult"
    # srcPath = "C:\\Users\\asus\\OneDrive - purdue.edu\\RealtimeProject\\Experiment1-Pilot\\UI07\\raw_txt"
    # dstPath = "C:\\Users\\asus\\OneDrive - purdue.edu\\RealtimeProject\\Experiment1-Pilot\\UI07\\pyprep_edf"
    # srcPath = r"C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\08-AnirudhCollection\2021-03-15_19h.03m.55s_anirudhmanual01"
    # dstPath = r"C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\08-AnirudhCollection\2021-03-15_19h.03m.55s_anirudhmanual01"
    # use_pyprep(srcPath,srcPath)

    path_list2 = [Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\01-JuanCollection2\2021-03-18_11h.37m.39s_juan-s2-autonomy01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\01-JuanCollection2\2021-03-18_11h.46m.27s_juan-s2-manual01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\06-KeyuCollection\2021-03-14_12h.24m.47s_keyu_P_manual_T_02'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\06-KeyuCollection\2021-03-14_12h.31m.16s_keyu_P_autonomy_T_02'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\08-AnirudhCollection\2021-03-15_18h.44m.15s_anirudhAutonomy01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\08-AnirudhCollection\2021-03-15_19h.03m.55s_anirudhmanual01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\07-JingCollection\2021-03-14_13h.02m.49s_jing-manual-01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\07-JingCollection\2021-03-14_13h.12m.14s_jing-autonomy-01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\05-ChihoCollections\2021-03-13_19h.42m.56s_Chiho_P_Manual_T_02'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\05-ChihoCollections\2021-03-13_19h.37m.20s_Chiho_P_Autonomy_T_02'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\04-GleboCollection\2021-03-12_20h.28m.48s_glebo_P_Manual_T_01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\04-GleboCollection\2021-03-12_20h.16m.57s_glebo_P_Autonomy_T_01'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\03-PauCollection\2021-03-12_13h.30m.25s_pau_P_Manual_T_02'),
                  Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\03-PauCollection\2021-03-12_13h.18m.14s_pau_P_Autonomy_T_02'), ]

    for p in path_list2:
        print(str(p))
        use_pyprep(p,p)

if __name__ == "__main__":
   main()

