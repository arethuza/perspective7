import logging
import cherrypy
import json
from worker import ServiceException
from processor import Processor

class PerspectiveService(object):

    def __init__(self, processor):
        self.processor = processor

    @cherrypy.expose
    def default(self, *dummy, **dummy2):
        """Handle all requests for all paths"""
        try:
            path = cherrypy.request.path_info
            verb = cherrypy.request.method.lower()
            login_response = self.processor.check_login(path, verb, cherrypy.request.params)
            if login_response is not None:
                # Request was successful attempt to log in
                return _serve_json(login_response, "")
        except ServiceException as exception:
            cherrypy.response.status = exception.response_code
            return exception.message
        except Exception as exception:
            cherrypy.response.status = 500
            return "Unknown error"

    def _authenticate(self):
        pass


def _serve_json(data, content_type):
    """ Serialize the supplied data as JSON """
    cherrypy.response.headers['Content-Type'] = content_type
    return json.dumps(data, indent=4, sort_keys=True).encode("utf-8")

if __name__ == '__main__':
    LOCATOR = "pq://postgres:password@localhost/perspective"
    processor = Processor(LOCATOR)
    if processor.requires_init_data():
        processor.load_init_data()
    processor.execute("/users/system", "post", "/users/system", { "password": "password"})
    service = PerspectiveService(processor)
    cherrypy.quickstart(service)