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

from experiment import ExperimentRunner

HOST_NAME = os.environ.get('HOST_NAME', '')
PORT_NUMBER = int(os.environ.get('PORT_NUMBER', 8080))
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')

runner = ExperimentRunner()


def post_request(url, post_body):
    print("proxy post request to: %s" % url)
    requests.post(url, post_body)


class Server(BaseHTTPRequestHandler):

    experiment = ExperimentRunner()

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
            action_value = test_data['actions'][0]['value']
            print("action: ", action_value)
            if self.path.startswith('/slack/proxy'):
                blocks = test_data['message']['blocks']
                url = None
                for i in test_data['message']['blocks']:
                    if i['type'] != 'actions':
                        continue
                    for e in i['elements']:
                        if e['value'] != action_value:
                            continue
                        url = e['url']
                        break
                if url:
                    post_request(url, post_body)
            elif self.path.startswith('/slack/interactive'):
                    if action_value == 'suggestion_1_on':
                        self.experiment.run_runbook()
                    elif action_value == 'suggestion_1_explain':
                        self.experiment.explain_runbook()
            else:
                handler = BadRequestHandler()
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