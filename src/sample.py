import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from anomaly import AnomalyDetection

from datetime import datetime

k1 = '#DC7633'
k2 = '#E74C3C'


def main(filename, experiment='exp1', columns=['pgz']):
    df = pd.read_csv(filename)
    ad = AnomalyDetection(45)
    for column in columns:
        filename = '{}_{}.png'.format(experiment, column)
        M = df[column].mean()
        ts = df[column].fillna(M).values
        ranges, positions = ad.find_anomalies(ts)
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.plot(np.arange(ts.shape[0]), ts)
        for k in ranges.keys():
            if len(ranges[k]) > 0:
                for start, end in ranges[k]:
                    c = k1 if k ==1 else k2
                    ax.axvspan(start, end-1, color=c, alpha = 0.16 * k)

        plt.savefig(filename)

if __name__ == '__main__':
    main('../data/stocks.csv', 'exp1', ['pgz', 'eia', 'lscc'])