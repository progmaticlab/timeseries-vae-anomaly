import time
import os
import sys
import requests

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

import urllib
import json

from response.staticHandler import StaticHandler
from response.imageHandler import ImageHandler
from response.badRequestHandler import BadRequestHandler
from response.okHandler import OkHandler
from response.slackHandler import SlackHandler
from response.accessDeniedHandler import AccessDeniedHandler

from experiment import ExperimentRunner


HOST_NAME = os.environ.get('HOST_NAME', '')
PORT_NUMBER = int(os.environ.get('PORT_NUMBER', 8080))
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')

APPROVED_APPS_TOKENS = os.environ.get('APPROVED_APPS_TOKENS', ':').split(':')

APPROVED_APPS = [
    {
        'name': 'skynet',
        'app_id': 'AU73B5P24',
        'client_id': '959111601632.959113193072',
        'verification_token': APPROVED_APPS_TOKENS[0]
    },
    {
        'name': 'Shadowcat',
        'app_id': 'AUP4CEVEY',
        'client_id': '917543802743.975148505508',
        'verification_token': APPROVED_APPS_TOKENS[1]
    }
]

def post_request(url, post_body):
    print("proxy post request to: %s" % url)
    requests.post(url, post_body)


def check_auth(payload):
    # TODO: check app against APPROVED_APPS
    return True


class Payload(object):
    def __init__(self, action, data):
        self._action = action
        self._data = data
    
    @property
    def action(self):
        return self._action


class Server(BaseHTTPRequestHandler):

    experiment = ExperimentRunner()
    interactive_responses = list()
    max_payloads = 100

    def __register_payload(self, action_value, payload):
        p = Payload(action_value, payload)
        self.interactive_responses.append(p)
        while len(self.interactive_responses.append) > self.max_payloads:
            self.interactive_responses.pop(0)

    def __pop_payload(self):
        try:
            return self.self.interactive_responses.pop(0)
        except:
            pass
        return None

    def do_HEAD(self):
        return

    def do_POST(self):
        print('{} POST received '.format(self.path))
        handler = None
        print('{} slack command received'.format(self.path))
        if self.path.startswith('/slack/'):
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length).decode("utf-8")
            payload = post_body.replace('payload=', '')
            payload_unqoute = urllib.parse.unquote(payload)
            test_data = json.loads(payload_unqoute)
            print("payload: ", test_data)
            if check_auth(payload):
                action_value = test_data['actions'][0]['value']
                print("action: ", action_value)
                if self.path.startswith('/slack/proxy'):
                    self.__register_payload(action_value, test_data)
                    button, cmd, param, *_  = action_value.split(':', 2) + [None, None]
                    url = param if cmd == 'url' else None
                    if url:
                        post_request(url, post_body)
                    
                elif self.path.startswith('/slack/interactive'):
                        action_value, incident, *_ = action_value.split(':', 1) + [None]
                        if action_value == 'suggestion_1_on':
                            self.experiment.run_runbook()
                        elif action_value == 'suggestion_1_explain':
                            self.experiment.explain_runbook()
                else:
                    handler = BadRequestHandler()
            else:
                handler = AccessDeniedHandler()
        else:
            handler = BadRequestHandler()

        if handler:
            self.respond({
                'handler': handler
            })


    def do_GET(self):
        print('{} GET received '.format(self.path))
        split_path = os.path.splitext(self.path)
        request_extension = split_path[1]

        handler = None
        if request_extension == ".png" and self.path.startswith('/anomaly/image'):
            handler = ImageHandler()
            handler.find({'path': self.path})
        elif request_extension is ".py":
            handler = BadRequestHandler()
        elif self.path.startswith('/analysis/run'):
            self.experiment.run_experiment()
            handler = OkHandler()
        elif self.path.startswith('/analysis/response'):
            payload = self.__pop_payload()
            action = payload.action if payload else ''
            handler = OkHandler(content_type='text/plain', data=action)
        elif self.path.startswith('/slack/command'):
            print('{} slack command received'.format(self.path))
            handler = SlackHandler(self.experiment)
        else:
            handler = StaticHandler()
            handler.find(self.path)

        if handler:
            self.respond({
                'handler': handler
            })

    def handle_http(self, handler):
        status_code = handler.getStatus()

        self.send_response(status_code)

        if status_code is 200:
            content = handler.getContents()
            self.send_header('Content-type', handler.getContentType())
        else:
            content = "404 Not Found"

        self.end_headers()

        return bytes(content, 'UTF-8') if handler.getContentType() != 'image/png' else bytes(content)

    def respond(self, opts):
        response = self.handle_http(opts['handler'])
        self.wfile.write(response)


if __name__ == '__main__':
    if not SLACK_CHANNEL:
        print(time.asctime(), 'ERROR: SLACK_CHANNEL env variable is not provided')
        sys.exit(-1)
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(time.asctime(), 'Server UP for channel %s - %s:%s' % (SLACK_CHANNEL, HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))