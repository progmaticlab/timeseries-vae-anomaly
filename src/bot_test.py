import os
import sys

import time
import logging
import traceback

import slack


def test_block_with_text_format(client):
    client.api_call(
        "chat.postMessage", json={
            'channel': 'GUC3RNY2F',
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":
                            "Hello, :arrow_up: I am observing the following anomaly in your infrastructure \n" +
                            "Within last month we observed similar problem 8 times\n" +
                            "In 84% it was solved by replacing the problematic *review pod* [review-v3]"

                    }
                }
            ]
        }
    )


def test_block_with_buttons(client):
    client.api_call(
        "chat.postMessage", json={
            'channel': 'GUC3RNY2F',
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":
                            "Hello, :arrow_up: I am observing the following anomaly in your infrastructure \n" +
                            "Within last month we observed similar problem 8 times\n" +
                            "In 84% it was solved by replacing the problematic *review pod* [review-v3]"

                    }
                }, {
                    "type": "actions",
                    "block_id": "actions1",
                    "elements": [{
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Replace review-v3"
                        },
                        "style": "primary",
                        "value": "suggestion_1_on"
                    }, {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "More Context"
                        },
                        # "style": "primary",
                        "value": "more_context"
                    }, {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "I will fix myself"
                        },
                        "style": "danger",
                        "value": "operator_flow"
                    }, {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "This is not an anomaly"
                            },
                            # "style": "primary",
                            "value": "negative_case"
                    }]
                }
            ]
        }
    )


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='../logs/shadowcat.log',
                        level=logging.INFO)
    logging.info('Number of arguments {} '.format(len(sys.argv)))

    logging.info('Starting the bot')

    slack_client = slack.WebClient(os.environ.get('SHADOWCAT_BOT_TOKEN'))

    # slack_client.api_call(
    #     "chat.postMessage", json= {
    #         'channel': 'GUC3RNY2F',
    #         # 'channel': 'bot_test_channel',
    #         'text': 'Hello, I am here!'
    #     }
    # )

    test_block_with_buttons(slack_client)
