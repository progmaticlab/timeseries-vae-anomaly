import time
import os
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
PORT_NUMBER = os.environ.get('PORT_NUMBER', 8080)

runner = ExperimentRunner()

class Server(BaseHTTPRequestHandler):

    experiment = ExperimentRunner()

    def do_HEAD(self):
        return

    def do_POST(self):
        # print('{} POST received '.format(self.path))
        handler = None
        print('{} slack command received'.format(self.path))
        if self.path.startswith('/slack/interactive'):
            print('{} slack command received'.format(self.path))
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length).decode("utf-8")
            payload = post_body.replace('payload=', '')
            payload_unqoute = urllib.parse.unquote(payload)
            test_data = json.loads(payload_unqoute)
            print(test_data)
            try:
                action_value = test_data['actions'][0]['value']
                print(action_value)
                if action_value == 'suggestion_1_on':
                    self.experiment.run_runbook()
                elif action_value == 'suggestion_1_explain':
                    self.experiment.explain_runbook()
            except Exception as e:
                print(e)
        else:
            handler = BadRequestHandler()

        if handler:
            self.respond({
                'handler': handler
            })


    def do_GET(self):
        # print('{} GET received '.format(self.path))
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
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))