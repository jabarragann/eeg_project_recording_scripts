import pandas as pd
from pathlib import Path
from itertools import product
import statsmodels.api as sm
from statsmodels.formula.api import ols
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind


if __name__ == '__main__':
    p = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\Cognitive-metrics') / 'all_features.csv'
    df = pd.read_csv(p, index_col=0)


    for area, band in product(['frontal', 'parietal'], ['Theta', 'Alpha']):
        print(area,band)
        new_df = df.loc[(df['area']==area)]

        model = ols('{:} ~ C(condition) + C(user) + C(condition):C(user)'.format(band), data=new_df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print(anova_table)


    #ThetaF - AlphaP
    fig, ax = plt.subplots(1, 1)
    p2 = Path(r'C:\Users\asus\OneDrive - purdue.edu\ThesisDataset\Cognitive-metrics') / 'ratio_features.csv'
    ratio_df = pd.read_csv(p2)
    sns.boxplot(x="user", y="ratio", hue="condition", data=ratio_df, palette="Set3", ax=ax)
    plt.show()

    fig, axes = plt.subplots(2,2)
    axes= axes.reshape(-1)
    for (area, band), ax  in zip(product(['frontal', 'parietal'], ['Theta', 'Alpha']), axes):
        # ax = axes
        frontal = df.loc[(df['area']=='parietal')]
        sns.boxplot(x="user", y="Alpha", hue="condition", data=df, palette="Set3", ax =ax)
        ax.set_title("{:} {:}".format(area, band))
    plt.show()
    x=0

