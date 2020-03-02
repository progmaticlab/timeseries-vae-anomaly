from response.requestHandler import RequestHandler

SAMPLES_FOLDER = '/Users/dmitry/pros/ngcops-pro/timeseries-vae-anomaly/samples'

class ImageHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'image/png'

    def find(self, routeData):
        try:
            path = routeData['path']
            image = path.replace('/anomaly/image', '')[1:]
            file = open('{}/{}'.format(SAMPLES_FOLDER, image), 'rb')
            self.contents = file
            self.setStatus(200)
            return True
        except Exception as e:
            print(e)
            self.setStatus(404)
            return False