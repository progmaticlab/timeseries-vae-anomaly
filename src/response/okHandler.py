import io

from response.requestHandler import RequestHandler

class OkHandler(RequestHandler):
    def __init__(self, data="Ok", content_type='text/plain'):
        super().__init__()
        self.contentType = content_type
        self.contents = io.StringIO(data)
        self.setStatus(200)
