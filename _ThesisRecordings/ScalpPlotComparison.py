from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from itertools import product
from _ThesisRecordings.ScalpPlotUtils import create_scalp_plot, create_comparison_scalp_plot, create_comparison_scalp_plot_v2

def reduce_size(df, min_size):
    results = []
    np.random.seed(10)
    for c in ['manual','autonomy']:
        p = df.loc[df[('info','condition')] == c]

        if p.shape[0]>min_size:
            remove_n = p.shape[0] - min_size
            drop_indices = np.random.choice(p.index, remove_n, replace=False)
            p = p.drop(drop_indices)
        results.append(p)

    return pd.concat(results).reset_index(drop=True)

def calculate_cognitive_metrics(path_list):
    feat_df = []
    for p in path_list:
        file = list(p.rglob("*eeg_features_full_set.pd"))[0]
        print(file.parent)
        feat_df.append(pd.read_pickle(file))

    feat_df = pd.concat(feat_df)
    feat_df = feat_df.reset_index(drop=True)

    # balance features
    min_size = min(feat_df.loc[feat_df[('info','condition')] == 'manual'].shape[0],
                   feat_df.loc[feat_df[('info','condition')] == 'autonomy'].shape[0])
    feat_df = reduce_size(feat_df, min_size)


    # create_comparison_scalp_plot_v2(feat_df, v_min=0.150,v_max=0.5)
    # print(feat_df[('info', 'user')].values[0])
    # plt.show()

    return feat_df

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

def main():

    feat_final = []
    for idx in range(0,len(path_list2),2):
        print(idx)
        p_l = path_list2[idx:idx+2]
        feat = calculate_cognitive_metrics(p_l)
        feat_final.append(feat)

    feat_final = pd.concat(feat_final)
    feat_final.reset_index(inplace=True)

    create_comparison_scalp_plot_v2(feat_final, v_min=0.150, v_max=0.5)
    plt.show()


    #Histogram
    data = feat_final.loc[:, pd.IndexSlice[['AF3', 'AF4', 'F3', 'Fz', 'F4', 'FC1', 'FC2'], 'Theta']].mean(axis=1)
    conditions = feat_final.loc[:, ('info','condition')]
    hist_df = pd.DataFrame(zip(data,conditions),columns=['data','conditions'])
    import seaborn as sns
    sns.histplot(hist_df,x='data',hue='conditions')
    plt.show()

    a = hist_df.loc[(hist_df['conditions'] == 'manual'),'data']
    b = hist_df.loc[(hist_df['conditions'] == 'autonomy'),'data']
    t, p = ttest_ind(a, b)
    print(t,p)
    print('manual',a.mean(),'autonomy',b.mean())
    x=0

    # parietal_ch = list(map(renameChannels, ["P7", "P3", "PZ", "P4", "P8", "PO4", "PO3"]))
    # frontal_ch = list(map(renameChannels, ["F7", "F3", "FZ", "F4", "F8", "FC1", "FC2"]))


if __name__ == "__main__":
   main()


