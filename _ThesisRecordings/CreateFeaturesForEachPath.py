from pathlib import Path
from scipy.signal import welch
import pandas as pd
import re
from _ThesisRecordings.CreateEegFeatures import create_cognitive_reduce_features
from _ThesisRecordings.CreateEegFeaturesFullSet import create_cognitive_full_features

if __name__ == "__main__":

    path_list = [Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\01-JuanCollection2\2021-03-18_11h.37m.39s_juan-s2-autonomy01'),
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

    for p in path_list:
        create_cognitive_reduce_features(p)
        create_cognitive_full_features(p)