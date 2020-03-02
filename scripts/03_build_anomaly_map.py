import pandas as pd
import json

import numpy as np

from src.anomaly import AnomalyDetection

def main(in_f, out_f):
    df = pd.read_csv(in_f)
    df.set_index('Unnamed: 0', inplace=True)
    print(df.shape)

    result = {}
    ad = AnomalyDetection(24)

    for c in df.columns:
        M = df[c].mean()
        ts = df[c].fillna(M).values
        ranges, positions = ad.find_anomalies(ts)
        anom = 0
        for k, rs in ranges.items():
            for range in rs:
                anom += range[1] - range[0]

        if anom != 0:
            print("For metric {}, ranges are {} with positions {}".format(c, ranges, positions))
            result[c] = {
                'pod': get_pod(c),
                'service': get_service(c),
                'metric': get_metric(c),
                'ranges': ranges,
                'positions': positions
            }

    with open(out_f, 'w') as outfile:
        json.dump(result, outfile)


def get_metric(s):
    return s.split(':')[1]


def get_service(s):
    return s.split('-')[0]


def get_pod(s):
    return '-'.join(s.split('-')[:2])

if __name__ == '__main__':
    main('/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/metrics_0_filter.csv', '../data/anomaly.json')