import falcon
import logging
from wsgiref import simple_server

from api_client.utility import StorageEngine, StorageError


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class NetworkCompilerClient(object):

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger('thingsapp.' + __name__)

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        try:
            doc = req.media
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')

        proper_thing = self.db.resolve_network(doc)
        resp.status = falcon.HTTP_201
        # resp.location = '/%s/things/%s' % (user_id, proper_thing['id'])
        resp.body = proper_thing


class Schema2Context(object):

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger('thingsapp.' + __name__)

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        try:
            doc = req.media
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')

        proper_thing = self.db.create_context(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


class FullSemDiffProcessor(object):

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger('thingsapp.' + __name__)

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        try:
            doc = req.media
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')

        proper_thing = self.db.create_full_sem_diff(doc)
        resp.status = falcon.HTTP_201
        resp.body = proper_thing


"""
# Configure your WSGI server to load "things.app" (app is a WSGI callable)
app = falcon.API(middleware=[
    AuthMiddleware(),
    RequireJSON(),
    JSONTranslator(),
])
"""
app = falcon.API()
database = StorageEngine()

network_resolver = NetworkCompilerClient(database)
context_creator = Schema2Context(database)
semDiff_processor = FullSemDiffProcessor(database)
app.add_route('/resolve_network', network_resolver)
app.add_route('/create_context', context_creator)
app.add_route('/semDiff', semDiff_processor)
# app.add_route('/{user_id}/things', things)

# If a responder ever raised an instance of StorageError, pass control to
# the given handler.
app.add_error_handler(StorageError, StorageError.handle)

# Proxy some things to another service; this example shows how you might
# send parts of an API off to a legacy system that hasn't been upgraded
# yet, or perhaps is a single cluster that all data centers have to share.
# sink = SinkAdapter()
# app.add_sink(sink, r'/search/(?P<engine>ddg|y)\Z')


if __name__ == '__main__':
    httpd = simple_server.make_server('localhost', 8000, app)
    httpd.serve_forever()
