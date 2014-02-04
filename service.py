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
            else:
                user_handle = self._authenticate()
                file_data = None
                if "wsgi.input" in cherrypy.request.wsgi_environ:
                    file_data = cherrypy.request.wsgi_environ['wsgi.input'].read()
                    cherrypy.request.params["_file_data"] = file_data
                response = self.processor.execute(path, verb, user_handle, cherrypy.request.params)
                return _serve_json(response, "")
        except ServiceException as exception:
            cherrypy.response.status = exception.response_code
            return exception.message
        except Exception as exception:
            cherrypy.response.status = 500
            return "Unknown error"

    def _authenticate(self):
        if "Authorization" not in cherrypy.request.headers:
            raise ServiceException(403, "Request must contain Authorization header")
        authorization_header = cherrypy.request.headers["Authorization"]
        a = authorization_header.split(" ")
        if len(a) != 2 or a[0] != "bearer":
            raise ServiceException(403, "Invalid format for Authorization header")
        token_value = a[1]
        user_handle = processor.get_user_for_token(token_value)
        if user_handle is None:
            raise ServiceException(403, "Note a valid authentication token")
        return user_handle


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