from response.requestHandler import RequestHandler

class SlackHandler(RequestHandler):
    def __init__(self, exp):
        super(SlackHandler, self).__init__()
        self.exp = exp

    def execute(self, path):
        command = path.replace('/slack/command/', '')
        self.setStatus(200)
        if command == 'suggestion_1_on':
            self.exp.run_runbook()
        elif command == 'explain_runbook':
            self.exp.explain_runbook()
        else:
            self.setStatus(404)
