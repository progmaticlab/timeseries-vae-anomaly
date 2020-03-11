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


# returns max of time services length
def get_period_lenght(anomaly_data):
    first = list(anomaly_data.keys())[0]
    ts = list(anomaly_data[first]['ts'])
    pl = len(ts)
    for k, v in anomaly_data.items():
        npl = len(v['ts'])
        if npl > pl:
            pl = npl
    return pl


class Aggregator(object):

    def __init__(self,
                 anomaly_data,
                 period_length=None,
                 causal_sensitivity=None):
        self.anomaly_data = anomaly_data
        self.period_length = period_length if period_length is not None else get_period_lenght(anomaly_data)
        self.causal_sensitivity = causal_sensitivity if causal_sensitivity is not None else self.period_length * 10 / 100
        self.relevance_decay = 1
        print("Aggregator: period_length=%s, causal_sensitivity=%s" % (self.period_length, self.causal_sensitivity))

    def __filter_metrics(self, m):
        if '|P' in m:
            return True if '|P99' in m or '|P95' in m else False
        return True

    def __relevance_function(self, anomaly_obj):
        ranges = anomaly_obj['ranges']
        relevance = 0
        for tpe, range in ranges.items():
            for r in range:
                for index in np.arange(r[0], r[1]):
                    relevance += float(tpe) / ((self.period_length - index) * self.relevance_decay)
        return relevance

    def build_time_relevance_report(self):
        report = []
        for metric, metric_obj in self.anomaly_data.items():
            # TODO: metrics are filtered at monitor side
            # if 'internal' in metric or 'external' in metric or 'http' not in metric:
            #     continue
            if self. __filter_metrics(metric):
                relevance = self.__relevance_function(metric_obj)
                report.append((metric, relevance))
            else:
                print("skipped filtered metric: %s" % metric)
        report = sorted(report, key=lambda x: -x[1])
        return report

    def build_incidents_report(self):
        relevance_report = self.build_time_relevance_report()
        incidents_report = {}
        for i in range(len(relevance_report)):
            added = False
            for key, incident_obj in incidents_report.items():
                if not added:
                    added = self.__add_to_incindent(incident_obj, relevance_report[i])

            if not added:
                self.__create_incident(incidents_report, relevance_report[i])
        return incidents_report, relevance_report


    def __add_to_incindent(self, incident_obj, report_item):
        incident_range = incident_obj.get('range') or []
        added = False
        for key, ranges in self.anomaly_data[report_item[0]].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - self.causal_sensitivity) < range[1] < (incident_range[1] + self.causal_sensitivity):
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    metric_name = self.__get_short_metric_name(report_item[0])
                    if metric_name not in incident_obj['metrics']:
                        incident_obj['metrics'].append(metric_name)
                        # incident_obj['metrics_set'].add(metric_name)
                    added = True
                else:
                    print("__add_to_incindent: skipped range=%s for report_item=%s" % (str(range), str(report_item)))

        if added:
            incident_obj['range'] = incident_range
            # TODO: hack for demo: patch pod to review till logic be added to reporter
            pod = self.anomaly_data[report_item[0]].get('pod')
            if pod and 'product' in incident_obj['pod'] and 'review' in pod:
                incident_obj['pod'] = pod

            print("__add_to_incindent: added report_item=%s" % str(report_item))
        else:
            print("__add_to_incindent: skipped report_item=%s" % str(report_item))
        return added

    def __get_short_metric_name(self, s):
        return s.split('|', 1)[1]

    def __create_incident(self, incidents_report, report_item):
        incident_range = [self.period_length, self.period_length]
        added = False
        incident_obj = {}
        for _, ranges in self.anomaly_data[report_item[0]].get('ranges').items():
            for range in ranges:
                if (incident_range[0] - self.causal_sensitivity) < range[1] < (incident_range[1] + self.causal_sensitivity):
                    incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]
                    if not added:
                        inc_uuid = random.randint(1000000, 9000000)
                        print('New incident is created {}'.format(inc_uuid))
                        metric_name = self.__get_short_metric_name(report_item[0])
                        incident_obj = {
                            'id': inc_uuid,
                            'range': incident_range,
                            'metrics': [metric_name],
                            # 'metrics_set': set([metric_name]),
                            'pod': self.anomaly_data[report_item[0]].get('pod'),
                            'service': self.anomaly_data[report_item[0]].get('service'),
                        }
                        incidents_report[inc_uuid] = incident_obj
                        added = True
                    else:
                        incident_range = [min(incident_range[0], range[0]), max(incident_range[1], range[1])]                         
                        # For more than 1 anomaly detected we don't need to add metrics again,
                        # just need to have a correct range
                        # incident_obj['metrics'].append(report_item[0])
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
        self.pod2metric_prefix_map = {}
        # update sibling map from anomaly data
        for metric, ad in anomaly_data.items():
            sn = ad['service']
            if sn not in self.siblings_map:
                self.siblings_map[sn] = set()
            self.siblings_map[sn].add(ad['pod'])
            self.pod2metric_prefix_map[sn + '|' + ad['pod']] = metric.split('|', 1)[0]

        # hack: dublicate product as productpage and viceversa
        if 'product' in self.siblings_map and 'productpage' not in self.siblings_map:
            self.siblings_map['productpage'] = self.siblings_map['product']
        if 'productpage' in self.siblings_map and 'product' not in self.siblings_map:
            self.siblings_map['product'] = self.siblings_map['productpage']
        # end
        print("VisualizeReports: incidents_report=%s" % (self.incidents_report))
        print("VisualizeReports: siblings_map=%s" % (self.siblings_map))
        print("VisualizeReports: pod2metric_prefix_map=%s" % (self.pod2metric_prefix_map))

    def visualize_with_siblings(self, out_f):
        number_of_metrics = len(self.incidents_report.get('metrics'))
        print("number_of_metrics: ", number_of_metrics)
        fig, axx = plt.subplots(number_of_metrics, 1, sharex=True,
                                figsize=(9, 3 + 2 * number_of_metrics),
                                dpi=80)
        service = self.incidents_report.get('service')
        i = 0
        for metric in self.incidents_report.get('metrics'):
            if number_of_metrics > 1:
                self.__plot_metric(axx[i], service, metric)
            else:
                self.__plot_metric(axx, service, metric)
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

    def __plot_metric(self, ax, service, metric_code):
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        # exmaple of metric:
        # product|cluster.inbound|9080|http|productpage.default.svc.cluster.local.internal.upstream_rq_time|P75
        # parts = metric_code.split('|')
        # service = parts[4].split('.', 1)[0]
        # metric_id = parts[1:]

        ax.title.set_text(metric_code)
        ax.set_ylabel('ms')

        index = self.metric_values.index

        i = 0
        print("__plot_metric: service=%s, metric_code=%s" % (service, metric_code))
        for pod in self.siblings_map.get(service):
            print("__plot_metric: service=%s, metric_code=%s, pod=%s" % (service, metric_code, pod))
            full_metric_name = self.pod2metric_prefix_map[service + '|' + pod] + '|' + metric_code
            ts = self.metric_values.get(full_metric_name)
            if ts is None or len(ts) == 0:
                print("skipped " + full_metric_name)
                print(self.metric_values.keys())
                continue
            ax.plot(index, ts, color=colors[i], label=pod)
            i += 1

            anomaly_report = self.anomaly_data[full_metric_name]
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

