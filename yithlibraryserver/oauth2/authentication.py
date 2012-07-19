from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.compat import decodebytes, encodebytes, encode_header


def authenticate_client(request):
    """Returns the client application representing this request.

    Uses the Authorization header in Basic format to identify
    the client of this request against the set of registered
    applications on the server.
    """
    authorization = request.headers.get('Authorization')
    if authorization is None:
        raise HTTPUnauthorized()

    method, credentials = request.authorization
    if method.lower() != 'basic':
        raise HTTPUnauthorized()

    credentials = decodebytes(credentials.encode('utf-8'))
    credentials = credentials.decode('utf-8')
    client_id, client_secret = credentials.split(':')

    application = request.db.applications.find_one({
            'client_id': client_id,
            'client_secret': client_secret
            })

    if application is None:
        raise HTTPUnauthorized()

    return application


def auth_basic_encode(user, password):
    value = '%s:%s' % (user, password)
    value = 'Basic ' + encodebytes(value.encode('utf-8')).decode('utf-8')
    return encode_header(value)
