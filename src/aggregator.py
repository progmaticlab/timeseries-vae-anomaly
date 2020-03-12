import os
import json
import pandas as pd
import numpy as np

import uuid

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

import random

from datetime import datetime, timedelta


DATA_FOLDER = os.environ.get('DATA_FOLDER', '.')
SAMPLES_FOLDER = os.environ.get('SAMPLES_FOLDER', '.')

application_diagram = {
    'productpage': set(['reviews', 'details']),
    'reviews': set(['ratings']),
    'details': set()
}

k1 = '#DC7633'
k2 = '#E74C3C'

delta = timedelta(seconds=5)


def get_period_lenght_map(anomaly_data):
    pl_map = dict()
    for _, v in anomaly_data.items():
        srv = v['service']
        if srv not in pl_map:
            pl_map[srv] = {'period_length': 0, 'sensitivity': 0 }
        npl = len(v['ts'])
        if npl > pl_map[srv]['period_length']:
            pl_map[srv] = {'period_length': npl, 'sensitivity': npl * 10 / 100 }
    return pl_map


class Aggregator(object):

    def __init__(self, anomaly_data):
        self.anomaly_data = anomaly_data
        self.period_length_map = get_period_lenght_map(anomaly_data)
        self.relevance_decay = 1
        print("Aggregator: period_length_map=%s" % (self.period_length_map))

    def __filter_metrics(self, metric):
        # TODO: metrics are filtered at monitor side
        # if 'internal' in metric or 'external' in metric or 'http' not in metric:
        #     return False
        # TODO: end
        if '|P' in metric:
            return '|P99' in metric or '|P95' in metric
        return True

    def __relevance_function(self, anomaly_obj):
        ranges = anomaly_obj['ranges']
        relevance = 0
        period_length = self.period_length_map[anomaly_obj['service']]['period_length']
        for tpe, range in ranges.items():
            for r in range:
                for index in np.arange(r[0], r[1]):
                    relevance += float(tpe) / ((period_length - index) * self.relevance_decay)
        return relevance

    def build_time_relevance_report(self):
        report = []
        for metric, anomaly_obj in self.anomaly_data.items():
            if not self.__filter_metrics(metric):
                print("skipped filtered metric: %s" % metric)
                continue
            relevance = self.__relevance_function(anomaly_obj)
            report.append((metric, relevance))
        return sorted(report, key=lambda x: -x[1])

    def build_incidents_report(self):
        relevance_report = self.build_time_relevance_report()
        incidents_report = {}
        for report_item in relevance_report:
            added = False
            for key, incident_obj in incidents_report.items():
                if not added:
                    added = self.__add_to_incindent(incident_obj, report_item)
            if not added:
                self.__create_incident(incidents_report, report_item)
        return incidents_report, relevance_report

    def __add_to_incindent(self, incident_obj, report_item):
        incident_range = incident_obj.get('range') or []
        added = False
        metric_name = report_item[0]
        srv = self.anomaly_data[metric_name]['service']
        sensitivity = self.period_length_map[srv]['sensitivity']
        for key, ranges in self.anomaly_data[metric_name].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - sensitivity) < range[1] < (incident_range[1] + sensitivity):
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    if metric_name not in incident_obj['metrics']:
                        incident_obj['metrics'].append(metric_name)
                    added = True
                else:
                    print("__add_to_incindent: skipped range=%s for report_item=%s" % (str(range), str(report_item)))
        if added:
            incident_obj['range'] = incident_range
            print("__add_to_incindent: added report_item=%s" % str(report_item))
        else:
            print("__add_to_incindent: skipped report_item=%s" % str(report_item))
        return added

    def __create_incident(self, incidents_report, report_item):
        added = False
        incident_obj = {}
        incident_range = [0, 0]
        metric_name = report_item[0]
        srv = self.anomaly_data[metric_name]['service']
        period_length = self.period_length_map[srv]['period_length']
        incident_range = [period_length, period_length]
        sensitivity = self.period_length_map[srv]['sensitivity']
        for _, ranges in self.anomaly_data[metric_name].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - sensitivity) < range[1] < (incident_range[1] + sensitivity):
                    # update incident range
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    if added:
                        # For more than 1 anomaly detected we don't need to add metrics again,
                        # just need to have a correct range
                        # incident_obj['metrics'].append(metric_name)
                        continue
                    # create new incident object
                    inc_uuid = random.randint(1000000, 9000000)
                    incident_obj = {
                        'id': inc_uuid,
                        'range': incident_range,
                        'metrics': [metric_name]
                    }
                    print('New incident is created {}'.format(incident_obj))
                    incidents_report[inc_uuid] = incident_obj
                    added = True
                else:
                    print("__create_incident: skipped range=%s for report_item=%s" % (str(range), str(report_item)))
        if added:
            incident_obj['range'] = incident_range
            print("__create_incident: added report_item=%s" % str(report_item))
        else:
            print("__create_incident: skipped report_item=%s" % str(report_item))

        return added



class VisualizeReports(object):
    def __init__(self,
                 metric_values,
                 anomaly_data,
                 incident_report):
        self.metric_values = metric_values
        self.anomaly_data = anomaly_data
        self.incidents_report = incident_report
        self.siblings_map = {}
        for metric, ad in anomaly_data.items():
            service = ad['service']
            if service not in self.siblings_map:
                self.siblings_map[service] = dict()
            short_metric = self.anomaly_data[metric].get('metric')
            if short_metric not in self.siblings_map[service]:
                self.siblings_map[service][short_metric] = set()
            self.siblings_map[service][short_metric].add(metric)
        print("VisualizeReports: incidents_report=%s" % (self.incidents_report))
        print("VisualizeReports: siblings_map=%s" % (self.siblings_map))

    def visualize_with_siblings(self, out_f):
        number_of_graphs = 0
        for _, metrics in self.siblings_map.items():
            number_of_graphs += len(metrics)

        print("visualize_with_siblings: number_of_graphs: %s" % number_of_graphs)
        fig, axx = plt.subplots(number_of_graphs, 1, sharex=True,
                                figsize=(9, 3 + 2 * number_of_graphs), dpi=80)

        i = 0
        for service, metrics_map in self.siblings_map.items():
            for short_name, metrics in metrics_map.items():
                print("visualize_with_siblings: short_name: %s, metrics: %s" % (short_name, metrics))
                if number_of_graphs > 1:
                    self.__plot_metric(axx[i], service, short_name, metrics)
                else:
                    self.__plot_metric(axx, service, short_name, metrics)
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

    def __plot_metric(self, ax, service, short_metric_name, metrics):
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        ax.title.set_text(short_metric_name)
        ax.set_ylabel('ms')

        index = self.metric_values.index
        i = 0
        print("__plot_metric: service=%s, metrics_list=%s" % (service, metrics))
        for metric in metrics:
            pod = self.anomaly_data[metric]['pod']
            print("__plot_metric: service=%s, metric=%s, pod=%s" % (service, metric, pod))
            ts = self.metric_values.get(metric)
            if ts is None or len(ts) == 0:
                print("WARNING: skipped metric: anomalys.json mismatch with metrics_0_filter.csv" + metric)
                print(self.metric_values.keys())
                continue
            ax.plot(index, ts, color=colors[i], label=pod)
            i += 1

            anomaly_report = self.anomaly_data[metric]
            ranges = anomaly_report.get('ranges', [])
            for k in ranges.keys():
                if len(ranges[k]) > 0:
                    for start, end in ranges[k]:
                        kk = float(k)
                        c = k1 if kk == 1 else k2
                        print("mark range")
                        ax.axvspan(index[start], index[min(len(index), end) - 1], color=c, alpha=0.16 * float(kk))

        ax.grid()
        ax.legend()



if __name__ == '__main__':
    with open('{}/anomaly.json'.format(DATA_FOLDER), 'r') as f:
        an_data = json.load(f)
        agg = Aggregator(an_data)
        incidents, relevance = agg.build_incidents_report()

        metrics_df = pd.read_csv('{}/metrics_0_filter.csv'.format(DATA_FOLDER))
        for key, item in incidents.items():
            print("make viz for incident: %s" % key)
            visualisation = VisualizeReports(metrics_df, an_data, item)
            visualisation.visualize_with_siblings('{}/{}_vis.png'.format(SAMPLES_FOLDER, key))

        print('\n')
        print(relevance)
        print('\n')
        print(incidents)

