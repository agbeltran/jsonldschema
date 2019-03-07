# In order to use the JSONSchema-LD API, you first need to activate it in a separate python script
# You can then run queries on the different endpoints

# Let's first create a client
from wsgiref import simple_server
from api_client.client import create_client


if __name__ == '__main__':
    app = create_client()  # Create the client
    # Run the client forever
    httpd = simple_server.make_server('localhost', 8001, app)
    httpd.serve_forever()

# From there, all endpoints should be accessible.
# For more details on these endpoints, look at the example above.
