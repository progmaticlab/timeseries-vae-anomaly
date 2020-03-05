import os
import json
import pandas as pd
import numpy as np

import uuid

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

import random

from datetime import datetime, timedelta

SAMPLES_FOLDER = os.environ.get('SAMPLES_FOLDER')

application_diagram = {
    'productpage': set(['reviews', 'details']),
    'reviews': set(['ratings']),
    'details': set()
}

k1 = '#DC7633'
k2 = '#E74C3C'

delta = timedelta(seconds=5)

class Aggregator(object):

    def __init__(self,
                 period_length,
                 causal_sensitivity=3):
        self.period_length = period_length
        self.causal_sensitivity = causal_sensitivity
        self.relevance_decay = 1

    def __filter_metrics(self, m):
        if '_P' in m:
            return True if '_P95' in m else False
        return True

    def __relevance_function(self, anomaly_obj):
        ranges = anomaly_obj['ranges']
        relevance = 0
        for tpe, range in ranges.items():
            for r in range:
                for index in np.arange(r[0], r[1]):
                    relevance += float(tpe) / ((self.period_length - index) * self.relevance_decay)
        return relevance

    def build_time_relevance_report(self,
                                    anomaly_data,
                                    take=3,
                                    with_siblings=False):
        report = []
        for metric, metric_obj in anomaly_data.items():
            if self. __filter_metrics(metric):
                relevance = self.__relevance_function(metric_obj)
                report.append((metric, relevance))
        report = sorted(report, key=lambda x: -x[1])
        return report

    def build_incidents_report(self, data):
        anomaly_data = dict(data)
        relevance_report = self.build_time_relevance_report(anomaly_data)
        incidents_report = {}
        for i in range(len(relevance_report)):
            added = False
            for key, incident_obj in incidents_report.items():
                if not added:
                    added = self.__add_to_incindent(incident_obj, anomaly_data, relevance_report[i])

            if not added:
                self.__create_incident(incidents_report, anomaly_data, relevance_report[i])
        return incidents_report, relevance_report


    def __add_to_incindent(self, incident_obj, anomaly_data, report_item):
        incident_range = incident_obj.get('range') or []
        added = False
        for key, ranges in anomaly_data[report_item[0]].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - self.causal_sensitivity) < range[1] < (incident_range[1] + self.causal_sensitivity):
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    incident_obj['metrics'].append(report_item[0])
                    added = True

        if added:
            incident_obj['range'] = incident_range

        return added


    def __create_incident(self, incidents_report, anomaly_data, report_item):
        incident_range = [self.period_length, self.period_length]
        added = False
        for key, ranges in anomaly_data[report_item[0]].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - self.causal_sensitivity) < range[1] < (incident_range[1] + self.causal_sensitivity):
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    if not added:
                        inc_uuid = random.randint(1000000, 9000000)
                        print('New incident is created {}'.format(inc_uuid))
                        incident_obj = {
                            'id': inc_uuid,
                            'range': incident_range,
                            'metrics': [report_item[0]]
                        }
                        incidents_report[inc_uuid] = incident_obj
                        added = True
                    else:
                        incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                        incident_obj['metrics'].append(report_item[0])
        if added:
            incident_obj['range'] = incident_range

        return added



class VisualizeReports(object):
    def __init__(self,
                 metric_values,
                 anomaly_data,
                 incident_report):
        self.metric_values = metric_values
        self.anomaly_data = anomaly_data
        self.incidents_report = incident_report
        self.siblings_map = {
            # TODO: do something with names    
            'product': set(['product']),
            'ratings': set(['ratings']),
            'details': set(['details']),
            'reviews': set(['reviews', 'reviews', 'reviews'])
            # 'product': set(['productpage-v1']),
            # 'ratings': set(['ratings-v1']),
            # 'details': set(['details-v1']),
            # 'reviews': set(['reviews-v1', 'reviews-v2', 'reviews-v3'])
        }


    def visualize_with_siblings(self, out_f):
        number_of_metrics = len(self.incidents_report.get('metrics'))
        fig, axx = plt.subplots(number_of_metrics, 1, sharex=True,
                                figsize=(9, 3 + 2 * number_of_metrics),
                                dpi=80)
        i = 0
        for metric in self.incidents_report.get('metrics'):
            self.__plot_metric(axx[i], metric)
            i += 1

        label_period = int(self.metric_values.shape[0] / 10)

        xtick_location = self.metric_values.index.tolist()[::label_period]
        xtick_labels = self.__build_list_timestamps(xtick_location)
        plt.xticks(ticks=xtick_location, labels=xtick_labels, rotation=60, fontsize=12, horizontalalignment='center', alpha=.7)
        plt.yticks(fontsize=12, alpha=.7)

        plt.savefig(out_f)


    def __build_list_timestamps(self, indices):
        result = []
        now = datetime.now() - (20 * delta)
        last = indices[-1]
        for i in range(len(indices)):
            tick = now - delta * (last - indices[i])
            result.append(tick.strftime('%H:%M:%S'))

        return result



    def __plot_metric(self, ax, metric_code):
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        # TODO: something with parsing names..
        parts = metric_code.split('|', 1)
        app_tpe = parts[0]
        metric_id = parts[1]

        ax.title.set_text(metric_id)
        ax.set_ylabel('seconds')

        index = self.metric_values.index

        i = 0
        for pod in self.siblings_map.get(app_tpe):
            m_code = '{}|{}'.format(pod, metric_id)
            ts = self.metric_values[m_code]
            ax.plot(index, ts, color=colors[i], label=pod)
            i += 1

        anomaly_report = self.anomaly_data[metric_code]
        ranges = anomaly_report.get('ranges')
        for k in ranges.keys():
            if len(ranges[k]) > 0:
                for start, end in ranges[k]:
                    kk = float(k)
                    c = k1 if kk == 1 else k2
                    ax.axvspan(index[start], index[end - 1], color=c, alpha=0.16 * float(kk))

        ax.grid()
        ax.legend()



if __name__ == '__main__':
    agg = Aggregator(255, 10)
    with open('/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/anomaly.json', 'r') as f:
        an_data = json.load(f)
    incidents, relevance = agg.build_incidents_report(an_data)

    metrics_df = pd.read_csv('/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/data/metrics_0_filter.csv')
    for key, item in incidents.items():
        visualisation = VisualizeReports(metrics_df, an_data, item)
        visualisation.visualize_with_siblings('{}/{}_vis.png'.format(SAMPLES_FOLDER, key))

    print('\n')
    print(relevance)
    print('\n')
    print(incidents)

