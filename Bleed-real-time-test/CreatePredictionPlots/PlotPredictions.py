import matplotlib.pyplot as plt
import pickle
import numpy as np

if __name__ == "__main__":

    predictions = pickle.load(open("./predictionsHigh.pickle","rb"))
    # predictions = pickle.load(open("./predictionsLow.pickle","rb"))
    predictions = np.array(predictions)

    fig, axes = plt.subplots(1,1)

    x = list(range(predictions.shape[0]))
    colors = np.where(predictions > 0.5, 'y', 'k')
    axes.scatter(x, predictions, c=colors)
    plt.show()