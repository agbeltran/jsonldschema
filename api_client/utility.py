import json
import falcon
import requests

from jsonschema.validators import Draft4Validator
from jsonschema import SchemaError

from utils.compile_schema import resolve_schema_references, get_name, resolve_reference
from utils.schema2context import resolve_network, process_schema_name, create_context_template
from semDiff.fullDiff import FullSemDiff


class StorageEngine(object):

    """
    def get_things(self, marker, limit):
        return [{'id': str(uuid.uuid4()), 'color': 'green'}]

    def add_thing(self, thing):
        thing['id'] = str(uuid.uuid4())
        return thing
    """

    def resolve_network(self, schema):
        processed_schemas = {}
        schema_url = schema['schema_url']

        processed_schemas[get_name(schema_url)] = '#'
        return json.dumps(resolve_schema_references(
                          resolve_reference(schema_url),
                          processed_schemas,
                          schema_url), indent=4)

    def create_context(self, user_input):
        if 'schema_url' not in user_input.keys():
            raise falcon.HTTPError(falcon.HTTP_400,
                                   "Query error, no schema url was provided")
        elif 'vocab' not in user_input.keys() \
                or type(user_input["vocab"]) != dict or \
                not len(user_input['vocab']) > 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   "Query error, no vocabulary was provided ")
        else:

            output = {}
            network = resolve_network(user_input["schema_url"])

            for semantic_type in user_input['vocab']:
                output[semantic_type] = {}

            for schema in network.keys():
                schema_name = process_schema_name(network[schema]['id']).lower()
                local_context = create_context_template(network[schema],
                                                        user_input['vocab'],
                                                        schema_name)

                for vocab_name in local_context:
                    output[vocab_name][schema_name] = local_context[vocab_name]

            return json.dumps(output, indent=4)

    def create_full_sem_diff(self, user_input):
        sem_diff = FullSemDiff(user_input['mapping'],
                               user_input['network_1'],
                               user_input['network_2'])

        return json.dumps(sem_diff.twins, indent=4)

    def validate_schema(self, user_input):
        try:
            validation = Draft4Validator.check_schema(json.loads(requests.get(user_input).text))
            if validation is not None:
                return json.dumps(validation, indent=4)
            else:
                return "You schema is valid"
        except Exception as e:
            return "Problem loading the schema: " + str(e)


class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        description = ('Sorry, couldn\'t write your thing to the '
                       'database. It worked on my box.')

        raise falcon.HTTPError(falcon.HTTP_725,
                               'Database Error',
                               description)


"""
class SinkAdapter(object):

    engines = {
        'ddg': 'https://duckduckgo.com',
        'y': 'https://search.yahoo.com/search',
    }

    def __call__(self, req, resp, engine):
        url = self.engines[engine]
        params = {'q': req.get_param('q', True)}
        result = requests.get(url, params=params)

        resp.status = str(result.status_code) + ' ' + result.reason
        resp.content_type = result.headers['content-type']
        resp.body = result.text


class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        account_id = req.get_header('Account-ID')

        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token, account_id):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token, account_id):
        return True  # Suuuuuure it's valid...


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


class JSONTranslator(object):
    # NOTE: Starting with Falcon 1.3, you can simply
    # use req.media and resp.media for this instead.

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in resp.context:
            return

        resp.body = json.dumps(resp.context['result'])
"""
