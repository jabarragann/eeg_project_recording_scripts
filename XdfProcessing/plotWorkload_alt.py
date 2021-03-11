from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    start_time = 669242.4432793272

    root_p = Path("./results/UJuan_SBloodValidation_T003_Baseline")

    # p1 = root_p / 'ExperimentMarkers_data.csv'
    # df2 = pd.read_csv(p1)
    # for i in range(df2.shape[0]):
    #     event = df2.loc[i, '1']
    #     if event == 'started':
    #         start_time = df2.loc[i, '0']
    #     plt.axvline(df2.loc[i, '0']- start_time, color='red')

    p1 = root_p / 'PredictionEvents_data.csv'
    df = pd.read_csv(p1)

    # plt.plot(df['0']- start_time,df['1'])
    # plt.plot(df['0']-df['0'][0],df['1'])
    # df2 = df.rolling(10, ).mean().fillna(0)
    df3 = df.rolling(40, ).mean().fillna(0)
    plt.plot(df['0'] - df['0'][0], df['1'])
    plt.plot(df['0'] - df['0'][0], df3['1'])

    p1 = root_p / 'MouseButtons_data.csv'
    df2 = pd.read_csv(p1)
    for i in range(df2.shape[0]):
        event = df2.loc[i,'1']
        if event == 'MouseButtonX2 pressed':
            plt.axvline(df2.loc[i,'0']- start_time+10, color='red')
            # plt.axvline(df2.loc[i, '0'] - start_time+20, color = 'green')


    plt.grid()

    plt.show()