from response.requestHandler import RequestHandler

class SlackHandler(RequestHandler):
    def __init__(self, exp):
        super().__init__()
        self.contentType = 'text/plain'

    def execute(self, path):
        command = path.replace('/slack/command/', '')
        self.setStatus(200)
        if command == 'run':
            exp.run_runbook()
        elif command == 'explain':
            exp.explain_runbook()
        else:
            self.setStatus(404)

