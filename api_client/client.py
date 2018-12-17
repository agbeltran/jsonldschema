import falcon
import logging
from wsgiref import simple_server

from api_client.utility import StorageEngine


def max_body(limit):
    """ Simple function to limit the size of the request

    :param limit: the maxiùum size of the request
    :type limit: int
    :return:
    """

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class ClientBase(object):
    """ The base class for all client classes
    .. warning:: Do not use

    :param db: the storage engine
    :type db: StorageEngine
    """

    def __new__(cls, db):
        if cls is ClientBase:
            raise TypeError("base class may not be instantiated")
        else:
            cls.db = db
            cls.logger = logging.getLogger('thingsapp.' + __name__)
        return object.__new__(cls)

    @staticmethod
    def get_request_body(req):
        try:
            return req.media
        except Exception:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')


class NetworkCompilerClient(ClientBase):
    """ Resolves all references and sub references for a given schema URL
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.resolve_network(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class Schema2ContextClient(ClientBase):
    """ Fully resolves a schema set from a given URL and
    creates the context template for each given ontology
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.create_context(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class FullSemDiffClient(ClientBase):
    """ Resolves the two given networks and compares their semantic
    values based on bound context files
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.create_full_sem_diff(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class SchemaValidatorClient(ClientBase):
    """ Validates a schema with the jsonschema library
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.validate_schema(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class InstanceValidatorClient(ClientBase):
    """ Validates a given instance against a given schema
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.validate_instance(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class NetworkValidatorClient(ClientBase):
    """ Resolves a network from given URL and validates each schema
    """

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        """ Process the get request

        :param req: the user request
        :param resp: the server response
        """
        doc = self.get_request_body(req)
        proper_thing = self.db.validate_network(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


"""
# Configure your WSGI server to load "things.app" (app is a WSGI callable)
app = falcon.API(middleware=[
    RequireJSON(),
    JSONTranslator(),
])

"""


def create_client():
    """
    Simple function that instantiates the app and creates the bridge to the API

    :return: the falcon app
    """
    application = falcon.API()
    database = StorageEngine()

    network_resolver = NetworkCompilerClient(database)
    context_creator = Schema2ContextClient(database)
    sem_diff_processor = FullSemDiffClient(database)
    schema_validator = SchemaValidatorClient(database)
    instance_validator = InstanceValidatorClient(database)
    network_validator = NetworkValidatorClient(database)

    application.add_route('/resolve_network', network_resolver)
    application.add_route('/create_context', context_creator)
    application.add_route('/semDiff', sem_diff_processor)
    application.add_route('/validate/schema', schema_validator)
    application.add_route('/validate/instance', instance_validator)
    application.add_route('/validate/network', network_validator)

    # application.add_error_handler(StorageError, StorageError.handle)

    return application


if __name__ == '__main__':
    app = create_client()
    httpd = simple_server.make_server('localhost', 8001, app)
    httpd.serve_forever()
