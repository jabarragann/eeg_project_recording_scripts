from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from itertools import product


def reduce_size(df, min_size):
    results = []
    np.random.seed(10)
    for c in ['manual','autonomy']:
        p = df.loc[df['condition'] == c]

        if p.shape[0]>min_size:
            remove_n = p.shape[0] - min_size
            drop_indices = np.random.choice(p.index, remove_n, replace=False)
            p = p.drop(drop_indices)
        results.append(p)

    return pd.concat(results).reset_index(drop=True)

def calculate_cognitive_metrics(path_list):
    feat_df = []
    for p in path_list:
        file = list(p.rglob("*eeg_features.csv"))[0]
        print(file.parent)
        feat_df.append(pd.read_csv(file, index_col=[0]))

    feat_df = pd.concat(feat_df)
    feat_df = feat_df.reset_index(drop=True)

    # balance features
    min_size = min(feat_df.loc[feat_df['condition'] == 'manual'].shape[0],
                   feat_df.loc[feat_df['condition'] == 'autonomy'].shape[0])
    feat_df = reduce_size(feat_df, min_size)

    #Concat features
    frontal_metrics = feat_df.loc[feat_df['area'] == 'frontal'].groupby(by=['condition']).mean()
    parietal_metrics = feat_df.loc[feat_df['area'] == 'parietal'].groupby(by=['condition']).mean()
    frontal_metrics['area'] = 'frontal'
    parietal_metrics['area'] = 'parietal'
    final = pd.concat([frontal_metrics, parietal_metrics])
    final['user'] = feat_df['user'].values[0]

    print("size of manual-autonomy: ", feat_df.loc[feat_df['condition'] == 'manual'].shape[0],
          feat_df.loc[feat_df['condition'] == 'autonomy'].shape[0])

    # for area, band in product(['frontal', 'parietal'], ['Theta', 'Alpha']):
    #     print(area, band)
    #     a = feat_df.loc[(feat_df['area'] == area) & (feat_df['condition'] == 'manual')][band]
    #     b = feat_df.loc[(feat_df['area'] == area) & (feat_df['condition'] == 'autonomy')][band]
    #     t, p = ttest_ind(a, b)
    #     print("pvalue {:0.003f} - is significant? {:}".format(p, p < 0.05))
    #
    # fig, axes = plt.subplots(2, 2)
    # for idx, area in zip(range(2), ['frontal', 'parietal']):
    #     sns.histplot(data=feat_df.loc[feat_df['area'] == area], x="Theta", hue="condition", ax=axes[idx, 0])
    #     sns.histplot(data=feat_df.loc[feat_df['area'] == area], x="Alpha", hue="condition", ax=axes[idx, 1])
    # plt.show()

    return final,feat_df

def calculate_ratio_metrics(path_list):
    ratio_df = []
    for p in path_list:
        file = list(p.rglob("*thetaf-alphap.csv"))[0]
        print(file.parent)
        ratio_df.append(pd.read_csv(file, index_col=[0]))

    feat_df = pd.concat(ratio_df)
    feat_df = feat_df.reset_index(drop=True)

    # balance features
    min_size = min(feat_df.loc[feat_df['condition'] == 'manual'].shape[0],
                   feat_df.loc[feat_df['condition'] == 'autonomy'].shape[0])
    feat_df = reduce_size(feat_df, min_size)

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
    final = []
    feat_final = []
    ratio_final = []
    for idx in range(0,13,2):
        print(idx)
        p_l = path_list2[idx:idx+2]
        df,feat = calculate_cognitive_metrics(p_l)
        ratio_df = calculate_ratio_metrics(p_l)
        final.append(df)
        feat_final.append(feat)
        ratio_final.append(ratio_df)

    final = pd.concat(final)
    feat_final = pd.concat(feat_final)
    ratio_final = pd.concat(ratio_final)

    final.reset_index(inplace=True)
    final.index.name = 'index'
    final_p = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\Cognitive-metrics')
    final.to_csv(final_p  / 'cog_metrics.csv')
    feat_final.to_csv(final_p / 'all_features.csv')
    ratio_final.to_csv(final_p / 'ratio_features.csv')

if __name__ == "__main__":
   main()


