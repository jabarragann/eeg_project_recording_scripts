import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne

mne.set_log_level("WARNING")

def renameChannels(chName):
    if 'Z' in chName:
        chName = chName.replace('Z','z')
    if 'P' in chName and 'F' in chName:
        chName = chName.replace('P','p')
    return chName

EEG_channels = list(map(renameChannels,["AF3","AF4","F7","F3","FZ","F4",
                                        "F8","FC5","FC1","FC2","FC6","T7","C3","CZ",
                                        "C4","T8","CP5","CP1","CP2","CP6","P7","P3",
                                        "PZ","P4","P8","PO3","PO4"]))

bands = ['Theta', 'Alpha','Beta']
titles = ["Theta [4-8Hz]","Alpha [8-12Hz]","Beta [12-30Hz]"]

def create_topo(data, fig_title, ax, v_min=-0.022, v_max=0.022):
    from mne.viz import plot_topomap

    mask = np.array([True for ch in EEG_channels])

    locations = pd.read_csv('./channel_2d_location.csv', index_col=0)
    locations['ch'] = locations.index.map(renameChannels)
    locations = locations.set_index('ch')
    locations = locations.loc[EEG_channels]
    # locations = locations.drop(index=["PO8", "PO7"])

    mask_params = dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                       linewidth=0, markersize=10)

    print("{:} Data max {:0.3f} Data min {:0.3f}".format(fig_title, data.max(), data.min()))

    im, cn = plot_topomap(data.values, locations[['x', 'y']].values,
                          outlines='head', axes=ax, cmap='jet', show=False,
                          names=EEG_channels, show_names=True,
                          mask=mask, mask_params=mask_params,
                          vmin=v_min, vmax=v_max, contours=7)
    ax.set_title(fig_title, fontsize=10)
    return im

def clean_axes(a):
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.spines["left"].set_visible(False)
    a.spines["bottom"].set_visible(False)
    a.set_xticks([])
    a.set_xticks([],minor=True)
    a.set_yticks([])
    a.set_yticks([],minor=True)

def create_scalp_plot(data, v_min=-0.5, v_max=0.5):
    fig, axes = plt.subplots(1, 4, figsize=(15, 5), gridspec_kw={'width_ratios': [3, 3, 3, 1]})
    axes = axes.reshape((-1, 1)).squeeze()

    for b,t,ax in zip(bands, titles,axes):
        d = data[pd.IndexSlice[:,b]]

        im = create_topo(d, t, ax, v_min=v_min, v_max=v_max)

    cbar = fig.colorbar(im, ax=axes[-1])
    clean_axes(axes[-1])

    ti = 'dB change from low state'
    cbar.ax.set_ylabel(ti, rotation=270, fontsize=10, labelpad=15)
    cbar.ax.yaxis.set_ticks_position('left')

    fig.tight_layout()


def create_comparison_scalp_plot(data_both_c, v_min=-0.5, v_max=0.5):
    fig, axes_grid = plt.subplots(2, 4, figsize=(15, 5), gridspec_kw={'width_ratios': [3, 3, 3, 1]})
    # axes_grid = axes.reshape((-1, 1)).squeeze()

    for idx, condition in enumerate(['manual','autonomy']):
        axes = axes_grid[idx,:].squeeze()
        all = data_both_c.mean(axis=0)
        d_min = all.min()
        d_max = all.max()

        data = data_both_c.loc[data_both_c[('info', 'condition')] == condition].mean(axis=0)
        for b,t,ax in zip(bands, titles,axes):
            d = data[pd.IndexSlice[:,b]]

            im = create_topo(d, t+condition, ax, v_min=d_min, v_max=d_max)

    cbar = fig.colorbar(im, ax=axes[-1])
    clean_axes(axes[-1])
    clean_axes(axes_grid[0,3])

    ti = 'dB change from low state'
    cbar.ax.set_ylabel(ti, rotation=270, fontsize=10, labelpad=15)
    cbar.ax.yaxis.set_ticks_position('left')

    fig.tight_layout()

def create_comparison_scalp_plot_v2(data_both_c, v_min=-0.5, v_max=0.5, convert_to_db=True):
    fig, axes_grid = plt.subplots(3, 3, figsize=(6, 12), gridspec_kw={'width_ratios': [5, 5, 1]})
    # axes_grid = axes.reshape((-1, 1)).squeeze()

    # if convert_to_db:
    #     data_both_c.loc[:,pd.IndexSlice[EEG_channels,:]] = 10*np.log10(data_both_c.loc[:,pd.IndexSlice[EEG_channels,:]])

    for idx, (b,t) in enumerate(zip(bands, titles)):
        axes = axes_grid[idx,:].squeeze()
        for ax_col, c in enumerate(['manual','autonomy']):

            # Individual limits for each band
            all = data_both_c.mean(axis=0).loc[pd.IndexSlice[:, b]]
            d_min = all.min()
            d_max = all.max()

            data = data_both_c.loc[data_both_c[('info', 'condition')] == c].mean(axis=0)
            d = data[pd.IndexSlice[:, b]]
            im = create_topo(d, t + c, axes[ax_col], v_min=d_min, v_max=d_max)

        cbar = fig.colorbar(im, ax=axes[-1])
        clean_axes(axes[-1])
        ti = 'Relative Band power'
        cbar.ax.set_ylabel(ti, rotation=270, fontsize=8, labelpad=12)
        cbar.ax.yaxis.set_ticks_position('left')

    fig.tight_layout()