import io

from response.requestHandler import RequestHandler

class OkHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/plain'
        file = io.StringIO("Ok") # takes string as arg
        self.contents = file
        self.setStatus(200)