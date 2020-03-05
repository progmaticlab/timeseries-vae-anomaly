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


DATA_FOLDER = os.environ.get('DATA_FOLDER')
SAMPLES_FOLDER = os.environ.get('SAMPLES_FOLDER')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')


class ExperimentRunner(object):

    def __init__(self):
        self.slack_client = slack.WebClient(os.environ.get('SHADOWCAT_BOT_TOKEN'))

    def run_experiment(self):
        agg = Aggregator(255, 10)
        with open('{}/anomaly.json'.format(DATA_FOLDER), 'r') as f:
            an_data = json.load(f)
        incidents, relevance = agg.build_incidents_report(an_data)

        metrics_df = pd.read_csv('{}/metrics_0_filter.csv'.format(DATA_FOLDER))
        for key, item in incidents.items():
            image_file = '{}_viz.png'.format(key)
            visualisation = VisualizeReports(metrics_df, an_data, item)
            visualisation.visualize_with_siblings('{}/{}'.format(SAMPLES_FOLDER, image_file))

            self.__upload_file('{}/{}'.format(SAMPLES_FOLDER, image_file), image_file)
            self.__run_incident_report_buttons(key, image_file)

    def run_runbook(self):
        self.slack_client.api_call(
            "chat.postMessage", json={
                'channel': SLACK_CHANNEL,
                'blocks': [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text":
                                "Jira Production Change management Ticket `JIRA-123` is created for this change\n" +
                                "All the operational steps will be reported to Ticketing system\n" +
                                "The resolution will be posted to this channel"

                        }
                    }
                ]
            })

    def explain_runbook(self):
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
                                " * create new instance of `reviews` pod\n" +
                                " * healthcheck for the new instance of `reviews` pod\n" +
                                " * route 3% of traffic to the new instance of  `reviews` pod\n" +
                                " * include the new instance of  `reviews` pod into load balancing pool \n" +
                                " * decommission corrupted instance of `reviews` pod"

                        }
                    }
                ]
            })

    def more_context(self):
        print('explain')


    def __upload_file(self, file_path, filename):
        self.slack_client.files_upload(channels=SLACK_CHANNEL, file=file_path, title=filename)


    def __run_incident_report_buttons(self, incident_key, filename):
        base_url = "{}://{}:{}/slack/interactive".format(SLACK_CALLBACK_SCHEMA, SLACK_CALLBACK_HOST, PORT_NUMBER)
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
                                "Within last month we observed similar problem 8 times\n" +
                                "In 84% cases it was solved by replacing the problematic *review pod* [review-v2]"

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
                            "value": "suggestion_1_on",
                            "url": "{}/command/run".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Read Suggested RunBook"
                            },
                            "style": "primary",
                            "value": "suggestion_1_explain",
                            "url": "{}/command/explain".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "More Context"
                            },
                            "style": "primary",
                            "value": "more_context",
                            "url": "{}/command/context".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "I will fix myself"
                            },
                            "style": "danger",
                            "value": "operator_flow",
                            "url": "{}/command/operator".format(base_url)
                        }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "This is not an anomaly"
                            },
                            "style": "primary",
                            "value": "negative_case",
                            "url": "{}/command/negative".format(base_url)
                        }]
                    }
                ]
            }
        )


if __name__ == '__main__':
    # exp = ExperimentRunner()
    # exp.run_experiment()
        agg = Aggregator(255, 10)
        with open('anomaly.json', 'r') as f:
            an_data = json.load(f)
        incidents, relevance = agg.build_incidents_report(an_data)

        metrics_df = pd.read_csv('metrics_0_filter.csv')
        for key, item in incidents.items():
            image_file = '{}_viz.png'.format(key)
            visualisation = VisualizeReports(metrics_df, an_data, item)
            visualisation.visualize_with_siblings('{}'.format(image_file))
