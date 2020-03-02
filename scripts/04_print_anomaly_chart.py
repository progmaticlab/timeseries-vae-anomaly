import pandas as pd
import json

import numpy as np
from matplotlib import pyplot as plt

from src.anomaly import AnomalyDetection

k1 = '#DC7633'
k2 = '#E74C3C'


def main(in_f, anomaly_file, metric):
    df = pd.read_csv(in_f)
    df.set_index('Unnamed: 0', inplace=True)
    # print(df.shape)

    M = df[metric].mean()
    ts = df[metric].fillna(M).values

    with open(anomaly_file, 'r') as f:
        an_data = json.load(f)
    ranges = an_data[metric]['ranges'] if metric in an_data else {}

    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    ax.plot(np.arange(ts.shape[0]), ts)
    for k in ranges.keys():
        if len(ranges[k]) > 0:
            for start, end in ranges[k]:
                c = k1 if k == 1 else k2
                ax.axvspan(start, end-1, color=c, alpha = 0.16 * int(k))

    plt.savefig('../samples/' + metric + '.png')

if __name__ == '__main__':
    main('/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/metrics_0.csv',
         '/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/anomaly.json',
         'productpage-v1-6cc647db65-f772m:cluster.outbound|9080||reviews.default.svc.cluster.local.upstream_rq_time_P95')