from response.requestHandler import RequestHandler

class SlackHandler(RequestHandler):
    def __init__(self, exp):
        super().__init__()
        self.contentType = 'text/plain'
        self.exp = exp

    def execute(self, path):
        command = path.replace('/slack/command/', '')
        self.setStatus(200)
        if command == 'run':
            self.exp.run_runbook()
        elif command == 'explain':
            self.exp.explain_runbook()
        else:
            self.setStatus(404)

