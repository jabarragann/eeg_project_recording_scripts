import pickle

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as col
import cv2

if __name__ == "__main__":

    predictions = pickle.load(open("./predictionsHigh.pickle","rb"))
    # predictions = pickle.load(open("./predictionsLow.pickle","rb"))
    predictions = np.array(predictions)
    fig, ax = plt.subplots(1,1, figsize=(1.5,2.0))
    fig.tight_layout()
    ax.set_xlim([-0.6,0.6])
    ax.set_ylim([0,1])
    cmapHigh = cm.ScalarMappable(col.Normalize(-0, 1), 'RdBu_r')
    cmapLow = cm.ScalarMappable(col.Normalize(-0, 1), 'RdBu')

    #Format the graph
    labels = [item.get_text() for item in ax.get_xticklabels()]
    xticks = [0,1,2,3]
    xtickslabels = ['','L','H','']

    # labels = [item.get_text() for item in ax.get_yticklabels()]
    # ytickslabels = [''] * len(labels)
    ax.set_yticks([0.0,0.5,1.0])
    # ax.set_title("Confidence")


    #Plot a graph to debug
    # values = [1-predictions[100],predictions[100],0]
    # colorForBars = np.array([cmapLow.to_rgba(1-predictions[100]),cmapHigh.to_rgba(predictions[100]),cmapHigh.to_rgba(0)])
    # ax.bar([-0.5,0,0.5],values, width=0.5, color=colorForBars)
    # plt.show()

    predictionsArray = np.zeros((predictions.shape[0], 200, 150, 3), dtype=np.uint8)

    ## Test
    values = [1 - predictions[0], predictions[0]]
    colorForBars = np.array([cmapLow.to_rgba(1 - predictions[0]), cmapHigh.to_rgba(predictions[0])])
    bar_cont = ax.bar([1, 2], values, width=1.0, color=colorForBars)

    # redraw the canvas
    ax.set_ylim([0, 1])
    ax.set_xticks(xticks)
    ax.set_xlim([0.0, 3])
    ax.set_xticklabels(xtickslabels)
    ax.set_yticks([0.0, 0.5, 1.0])

    for i in range(len(predictions)):
        print(i)

        bar_cont[0].set_height(1-predictions[i])
        bar_cont[1].set_height(predictions[i])
        bar_cont[0].set_color(cmapLow.to_rgba(1 - predictions[i]))
        bar_cont[1].set_color(cmapHigh.to_rgba(predictions[i]))

        #Create bar chart
        # ax.clear()
        # values = values = [1-predictions[i],predictions[i]]
        # colorForBars = np.array([cmapLow.to_rgba(1 - predictions[i]), cmapHigh.to_rgba(predictions[i])])
        # ax.bar([-0.5, 0], values, width=0.5, color=colorForBars)
        #
        # # redraw the canvas
        # ax.set_ylim([0, 1])
        # ax.set_xticks(xticks)
        # ax.set_xticklabels(xtickslabels)
        # ax.set_yticks([0.0, 0.5, 1.0])
        fig.canvas.draw()


        # Transform figure to image
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # img is rgb, convert to opencv's default bgr


        predictionsArray[i] = img
        print(img.shape)
        # display image with opencv or any operation you like
        cv2.imshow("plot", predictionsArray[i])
        #
        #
        k = cv2.waitKey(0)

    # pickle.dump({'img': predictionsArray}, open("./predictionsImg.pickle", "wb"))
    cv2.destroyAllWindows()