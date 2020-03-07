from response.requestHandler import RequestHandler

class AccessDeniedHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/plain'
        self.setStatus(403)