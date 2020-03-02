import time
import os
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

from response.staticHandler import StaticHandler
from response.imageHandler import ImageHandler
from response.badRequestHandler import BadRequestHandler

HOST_NAME = 'localhost'
PORT_NUMBER = 9898


class Server(BaseHTTPRequestHandler):

    def do_HEAD(self):
        return

    def do_POST(self):
        return

    def do_GET(self):
        split_path = os.path.splitext(self.path)
        request_extension = split_path[1]

        if request_extension == ".png" and self.path.startswith('/anomaly/image'):
            handler = ImageHandler()
            handler.find({'path': self.path})
        elif request_extension is ".py":
            handler = BadRequestHandler()
        else:
            handler = StaticHandler()
            handler.find(self.path)

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