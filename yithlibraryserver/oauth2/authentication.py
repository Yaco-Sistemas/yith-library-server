import base64

from pyramid.httpexceptions import HTTPUnauthorized


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

    credentials = bytes(credentials, 'utf-8')
    credentials = base64.decodebytes(credentials)
    credentials = credentials.decode('utf-8')
    client_id, client_secret = credentials.split(':')

    application = request.db.applications.find_one({
            'client_id': client_id,
            'client_secret': client_secret
            })

    if application is None:
        raise HTTPUnauthorized()

    return application


def is_app_authorized(request, user, app):
    user_obj = request.db.users.find_one({'user': user})
    return str(app['_id']) in user_obj['authorized_apps']


def store_user_authorization(request, user, app):
    request.db.users.update(
        {'user': user},
        {'$addToSet': {'authorized_apps': str(app['_id'])}},
        safe=True,
        )


def generate_grant_code(uri, scope, state):
    grant = 'grant'

    parameters = ['code=%s' % grant]
    if state:
        parameters.append('state=%s' % state)

    return '%s?%s' % (uri, '&'.join(parameters))


def generate_access_code():
    return 'access'
