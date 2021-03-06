import cherrypy
import json
import worker
from processor import Processor
from items.file_item import FileResponse
import performance as perf
import dbgateway

user_cache = {}

class PerspectiveService(object):

    def __init__(self, processor):
        self.processor = processor

    @cherrypy.expose
    def default(self, *dummy, **dummy2):
        """Handle all requests for all paths"""
        try:
            start = perf.start()
            path = cherrypy.request.path_info
            http_method = cherrypy.request.method.lower()
            login_response = self.processor.check_login(path, http_method, cherrypy.request.params)
            if login_response is not None:
                # Request was successful attempt to log in
                response = _serve_json(login_response, "post-login")
            else:
                user_handle = self._authenticate()
                file_data = None
                if http_method == "put" and "wsgi.input" in cherrypy.request.wsgi_environ:
                    file_data = cherrypy.request.wsgi_environ['wsgi.input'].read()
                    cherrypy.request.params["_file_data"] = file_data
                response, return_type = self.processor.execute(path, http_method, user_handle, cherrypy.request.params)
                if isinstance(response, FileResponse):
                    cherrypy.response.stream = True
                    cherrypy.response.headers["Content-Type"] = "application/octet-stream"
                    cherrypy.response.headers["Content-Disposition"] = 'attachment; filename="{0}"'.format(response.name)
                    cherrypy.response.headers["Content-Length"] = str(response.length)
                    response = response.block_yielder()
                else:
                    response = _serve_json(response, return_type)
            perf.end2("service", "default", start)
            return response
        except worker.ServiceException as exception:
            cherrypy.response.status = exception.response_code
            return exception.message
        except:
            # TODO make this a bit more sensible
            cherrypy.response.status = 500
            return "Unknown error"


    def _authenticate(self):
        start = perf.start()
        if "Authorization" not in cherrypy.request.headers and "token" not in cherrypy.request.params:
            raise worker.ServiceException(403, "Request must contain Authorization header or parameter")
        if "Authorization" in cherrypy.request.headers:
            authorization_header = cherrypy.request.headers["Authorization"]
            a = authorization_header.split(" ")
            if len(a) != 2 or a[0] != "Bearer":
                raise worker.ServiceException(403, "Invalid format for Authorization header")
            token_value = a[1]
        else:
            token_value = cherrypy.request.params["token"]
            del cherrypy.request.params["token"]
        if token_value in user_cache:
            user_handle = user_cache[token_value]
        else:
            user_handle = processor.get_user_for_token(token_value)
            user_cache[token_value] = user_handle
        if user_handle is None:
            raise worker.ServiceException(403, "Not a valid authentication token")
        perf.end(__name__, start)
        return user_handle


def _serve_json(data, content_type):
    """ Serialize the supplied data as JSON """
    cherrypy.response.headers['Content-Type'] = content_type
    return json.dumps(data, indent=4, sort_keys=True).encode("utf-8")

if __name__ == '__main__':
    dbgateway.locator = "pq://postgres:password@localhost/perspective"
    processor = Processor()
    if processor.requires_init_data():
        processor.load_init_data()
    processor.execute("/users/system", "post", "/users/system", { "password": "password"})
    service = PerspectiveService(processor)
    cherrypy.quickstart(service)