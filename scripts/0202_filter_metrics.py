import pandas as pd
import json

import numpy as np

def main(in_f, out_f):
    df = pd.read_csv(in_f)
    keep_columns = []
    for c in df.columns:
        if 'P95' in c and '.external' not in c:
            keep_columns.append(c)

    df[keep_columns].to_csv(out_f)

if __name__ == '__main__':
    main('/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/metrics_0.csv', '../data/metrics_0_filter.csv')