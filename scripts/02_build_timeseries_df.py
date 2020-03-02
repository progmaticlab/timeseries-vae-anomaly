import argparse

from os import listdir
from os.path import isfile, join

import pandas as pd

from datetime import datetime

DT_FORMAT= '%Y-%m-%dT%H:%M:%S'

gauges = ['_buffered', '_active', 'uptime', 'concurrency', '_allocated', '_size', '.live', '.state', '_connections',
          'version', '_expiring', '_epoch', '_clusters', '_clusters', '_healthy','_degraded', '_total',	'_weight',
          '.healthy', '_open', '_cx', '_pending', '_rq', '_retries', 	'.size', '_per_host', 'gradient', '_limit',
          '_size', '_msecs', '_faults', '_warming', '_draining', '_started', '_keys', '_layers', '.active', '_requests']

exclude_keys = ['version', 'istio', 'prometheus', 'grafana', 'nginx', 'kube', 'jaeger', 'BlackHole', 'grpc', 'zipkin', 'mixer']

def main(folder, output):
    metrics = {}

    for file in [f for f in listdir(folder) if isfile(join(folder, f))]:
        parts = file.split('.')
        if len(parts) == 2 and 'pods' != parts[0]:
            dt = datetime.strptime(parts[1][:19], DT_FORMAT)
            ts = int(dt.timestamp())
            with open(join(folder, file), 'r') as file:
                for line in file.read().splitlines():
                    metric_value = line.split(': ')
                    if filter_metrics(metric_value[0]):
                        metric_name = '{}:{}'.format(parts[0], metric_value[0])
                        if 'P0' in metric_value[1]:
                            percentiles = extract_p_values(metric_value[1])
                            for k, v in percentiles.items():
                                metric_p_name = metric_name + '_' + k
                                if metric_p_name not in metrics:
                                    metrics[metric_p_name] = {}
                                metrics[metric_p_name][ts] = v
                        else:
                            m_value = to_float(metric_value[1])
                            if m_value is not None:
                                if metric_name not in metrics:
                                    metrics[metric_name] = {}
                                metrics[metric_name][ts] = m_value

    print(len(metrics))
    df = pd.DataFrame()
    i = 0
    keys = list([k for k in metrics.keys()])
    sorted(keys, key=lambda x: x.split('|')[-1])

    for key in keys:
        tmp_df = pd.DataFrame.from_dict(metrics[key], orient='index')
        tmp_df.rename(columns={0: key}, inplace=True)
        if df.empty:
            df = tmp_df.copy(deep=True)
        else:
            df = df.join(tmp_df, how='outer')
        i+=1
        if i % 100 == 0:
            print(i)
            # df.to_csv(output + '.{}'.format(i))
            # df = pd.DataFrame()

    df.to_csv(output)

def extract_p_values(s):
    result = {}
    for percentiles in s.split(' '):
        parts = percentiles.split('(')
        p_code = parts[0]
        p_complex = parts[1][:-1]
        p_value = p_complex.split(',')[0]
        result[p_code] = to_float(p_value[0]) if p_value != 'nan' else 0.0

    return result

def filter_metrics(metric):
    if '9080' not in metric:
        return False

    if 'version' in metric:
        return False

    for exclude in exclude_keys:
        if exclude in metric:
            return False

    if is_gauge(metric):
        return False

    if '_rq_' not in metric:
        return False

    return True


def is_gauge(key):
    for item in gauges:
        if key.endswith(item):
            return True
    return False


def to_float(s):
    result = None
    try:
        result = float(s)
    except ValueError:
        print(s)
    return result


if __name__ == '__main__':
    # main('/Users/dmitry/pros/ngcops-pro/data/data', '../data/metrics.csv')

    parser = argparse.ArgumentParser()
    parser.add_argument('-path', help='metrics dir')
    parser.add_argument('-o', '--output', help='output file')
    args = parser.parse_args()

    main(args.path, args.output)