from response.requestHandler import RequestHandler

class SlackHandler(RequestHandler):
    def __init__(self, exp, pod=''):
        super(SlackHandler, self).__init__()
        self.exp = exp
        self.pod = pod

    def execute(self, path):
        command = path.replace('/slack/command/', '')
        self.setStatus(200)
        if command == 'suggestion_1_on':
            self.exp.run_runbook(pod=self.pod)
        elif command == 'suggestion_1_explain':
            self.exp.explain_runbook(pod=self.pod)
        else:
            self.setStatus(404)
