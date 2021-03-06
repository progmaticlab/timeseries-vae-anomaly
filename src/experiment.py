import os
import sys
import json

import pandas as pd

import time
import logging
import traceback

import slack

from aggregator import Aggregator
from aggregator import VisualizeReports


SLACK_CALLBACK_SCHEMA = os.environ.get('SLACK_CALLBACK_SCHEMA', 'http')
SLACK_CALLBACK_HOST = os.environ.get('SLACK_CALLBACK_HOST', 'localhost')
PORT_NUMBER = os.environ.get('PORT_NUMBER', 8080)


DATA_FOLDER = os.environ.get('DATA_FOLDER', '.')
SAMPLES_FOLDER = os.environ.get('SAMPLES_FOLDER', '.')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')

# for now filter all except reviews
def get_pod_for_buttons(an_data, incident):
    for metric in incident.get('metrics', []):
        if 'review' in an_data[metric].get('service', ''):
            return an_data[metric].get('pod')
    return None


def get_pods_list(an_data, incident):
    pods = list()
    for metric in incident.get('metrics', []):
        p = an_data[metric].get('pod')
        if p:
            pods.append(p)
    return pods


class ExperimentRunner(object):

    def __init__(self):
        self.slack_client = slack.WebClient(os.environ.get('SHADOWCAT_BOT_TOKEN'))

    def run_experiment(self):
        with open('{}/anomaly.json'.format(DATA_FOLDER), 'r') as f:
            an_data = json.load(f)
            agg = Aggregator(an_data)
            incidents, relevance = agg.build_incidents_report()
            metrics_df = pd.read_csv('{}/metrics_0_filter.csv'.format(DATA_FOLDER))
            for key, item in incidents.items():
                self.__do_report(metrics_df, an_data, key, item)

    def __do_report(self, metrics_df, an_data, key, item):
        image_file = '{}_viz.png'.format(key)
        visualisation = VisualizeReports(metrics_df, an_data, item)
        visualisation.visualize_with_siblings('{}/{}'.format(SAMPLES_FOLDER, image_file))
        pod = get_pod_for_buttons(an_data, item)
        print("Report incident %s for pod %s" % (key, pod))
        self.__upload_file('{}/{}'.format(SAMPLES_FOLDER, image_file), image_file)
        self.__run_incident_report_buttons(key, pod, image_file)

    def __do_report_with_pods_list(self, metrics_df, an_data, key, item):
        image_file = '{}_viz.png'.format(key)
        visualisation = VisualizeReports(metrics_df, an_data, item)
        visualisation.visualize_with_siblings('{}/{}'.format(SAMPLES_FOLDER, image_file))
        pods = get_pods_list(an_data, item)
        print("Report incident %s for pods %s" % (key, pods))
        self.__upload_file('{}/{}'.format(SAMPLES_FOLDER, image_file), image_file)
        self.__run_incident_report_selections(key, pods, image_file)

    def run_runbook(self, pod=''):
        self.slack_client.api_call(
            "chat.postMessage", json={
                'channel': SLACK_CHANNEL,
                'blocks': [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text":
                                "Problematic pod " + (pod if pod else "") + " is replaced.\n"
                                "Jira Production Change management Ticket `JIRA-123` is created for this change\n" +
                                "All the operational steps will be reported to Ticketing system\n" +
                                "The resolution will be posted to this channel"

                        }
                    }
                ]
            })

    def explain_runbook(self, pod=''):
        self.slack_client.api_call(
            "chat.postMessage", json={
                'channel': SLACK_CHANNEL,
                'blocks': [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text":
                                "Suggested Runbook consists of the following step\n" +
                                " * replace problematic pod " + (pod if pod else '') + "\n" +
                                " * create Jira ticket\n"
                        }
                    }
                ]
            })

    def __upload_file(self, file_path, filename):
        self.slack_client.files_upload(channels=SLACK_CHANNEL, file=file_path, title=filename)


    def __run_incident_report_buttons(self, incident_key, pod, filename):
        # base_url = "{}://{}:{}/slack/interactive".format(SLACK_CALLBACK_SCHEMA, SLACK_CALLBACK_HOST, PORT_NUMBER)
        self.slack_client.api_call(
            "chat.postMessage", json={
                'channel': SLACK_CHANNEL,
                'blocks': [
                    # {
                    #     "type": "image",
                    #     "title": {
                    #         "type": "plain_text",
                    #         "text": "Incident {}".format(incident_key),
                    #     },
                    #     # "image_url": "http://13.48.135.132:9898/anomaly/image/{}".format(filename),
                    #     "image_url": "https://drive.google.com/file/d/1ANQOjDsZnQnzcVQQysw_9K68W821Cq5A/view?usp=sharing",
                    #     "alt_text": "Image with Anomaly which is not available"
                    # },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text":
                                ":arrow_up: Incident {} is created with the following anomaly in your infrastructure \n".format(incident_key) +
                                "It could be solved by replacing the problematic pod {}".format(pod)

                        }
                    }, {
                        "type": "actions",
                        "block_id": "actions1",

                        "elements": [{
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Use Suggested RunBook"
                            },
                            "style": "primary",
                            "value": "suggestion_1_on:%s" % pod,
                            # "url": "{}/command/run".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Describe Suggested RunBook"
                            },
                            "style": "primary",
                            "value": "suggestion_1_explain:%s" % pod,
                            # "url": "{}/command/explain".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "I will fix myself"
                            },
                            "style": "danger",
                            "value": "operator_flow:%s" % pod,
                            # "url": "{}/command/operator".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "This is not an anomaly"
                            },
                            "style": "primary",
                            "value": "negative_case:%s" % pod,
                            # "url": "{}/command/negative".format(base_url)
                        }]
                    }
                ]
            }
        )

    def __get_suggestions(self, pods, action):
        suggestion_options = list()
        for p in pods:
            suggestion_options.append({
                "text": {
                    "type": "plain_text",
                    "text": "%s" % p,
                    "emoji": True
                },
                "value": "%s:%s" % (action, p),
            })
        return suggestion_options

    def __run_incident_report_selections(self, incident_key, pods, filename):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":arrow_up: Incident {} is created with the following anomaly in your infrastructure \n".format(incident_key) +
                    "It could be solved by replacing the problematic pod"
                }
            }, {
                "type": "divider"
            }, {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Replace problematic pod*"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select pod",
                        "emoji": True
                    },
                    "options": self.__get_suggestions(pods, 'suggestion_1_on'),
                    "confirm": {
						"title": {
							"type": "plain_text",
							"text": "Replace selecte pod?"
						},
						"text": {
							"type": "mrkdwn",
							"text": "The selected pod will be replaced with new one"
						},
						"confirm": {
							"type": "plain_text",
							"text": "Confirm"
						},
						"deny": {
							"type": "plain_text",
							"text": "No"
						}
					},
                }
            }, {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is not anomaly, mark pod as normal"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select pod",
                        "emoji": True
                    },
                    "options": self.__get_suggestions(pods, 'negative_case'),
                    "confirm": {
						"title": {
							"type": "plain_text",
							"text": "This is not anomaly?"
						},
						"text": {
							"type": "mrkdwn",
							"text": "The anomaly for selected pod will be marked as normal"
						},
						"confirm": {
							"type": "plain_text",
							"text": "Confirm"
						},
						"deny": {
							"type": "plain_text",
							"text": "No"
						}
					},
                }
            } , {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "`I will fix myself for pod`"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select pod",
                        "emoji": True
                    },
                    "options": self.__get_suggestions(pods, 'operator_flow'),
                    "confirm": {
						"title": {
							"type": "plain_text",
							"text": "This is not anomaly?"
						},
						"text": {
							"type": "mrkdwn",
							"text": "The anomaly for selected pod will be marked as normal"
						},
						"confirm": {
							"type": "plain_text",
							"text": "Confirm"
						},
						"deny": {
							"type": "plain_text",
							"text": "No"
						}
					},
                }
            },  {
                "type": "divider"
            }
        ]

        slack_data = {
            'channel': SLACK_CHANNEL,
            'blocks': blocks
        }

        print("ExperimentRunner::__run_incident_report_buttons: %s" % (slack_data))
        self.slack_client.api_call("chat.postMessage", json=slack_data)


if __name__ == '__main__':
    exp = ExperimentRunner()
    exp.run_experiment()
