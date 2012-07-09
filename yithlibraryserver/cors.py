class CORSManager(object):

    def __init__(self, allowed_origins):
        self.allowed_origins = allowed_origins.split(' ')

    def add_cors_header(self, request, response):
        if 'Origin' in request.headers:
            origin = request.headers['Origin']
            if origin in self.allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin

