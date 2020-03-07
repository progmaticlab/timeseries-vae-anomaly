import io

from response.requestHandler import RequestHandler

class OkHandler(RequestHandler):
    def __init__(self, content_type='text/plain', data="Ok"):
        super().__init__()
        self.contentType = content_type
        self.contents = io.StringIO(data)
        self.setStatus(200)
