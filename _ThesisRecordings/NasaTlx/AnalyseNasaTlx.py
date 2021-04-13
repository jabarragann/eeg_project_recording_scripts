import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_rel

if __name__ == '__main__':

    df = pd.read_csv('nasa_tlx_results.csv',header=[0], sep=',')

    final = pd.DataFrame(columns=['autonomy','manual','t statistic','p value'])
    for demand in df['demand'].unique():
        m = df.loc[(df['demand'] == demand) & (df['condition'] == 'manual')]['Score']
        a = df.loc[(df['demand'] == demand) & (df['condition'] == 'autonomy')]['Score']
        t, p = ttest_rel(a, m)
        print(demand, p,p<0.06)

        a_mean = a.mean();a_std = a.std()
        m_mean = m.mean();m_std = m.std()
        final.loc[demand] = ["{:.2f} ({:.2f})".format(a_mean,a_std),
                         "{:.2f} ({:.2f})".format(m_mean,m_std),
                         "{:.3f}".format(t),
                         "{:.3f}".format(p)]

    final.to_csv('./processed_nasa_tlx.csv')

    df1 = df.loc[~(df['demand'] == 'WorkloadScore')]
    df2 = df.loc[(df['demand'] == 'WorkloadScore')]
    ax = sns.boxplot(x="demand", y="Score", hue="condition", data=df1, palette="Set3")
    plt.legend(bbox_to_anchor=(0.9, 0.9))
    plt.show()
    print(0)