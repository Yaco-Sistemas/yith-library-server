import base64
import uuid

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
    return str(app['_id']) in user['authorized_apps']


def store_user_authorization(request, user, app):
    request.db.users.update(
        {'user': user['_id']},
        {'$addToSet': {'authorized_apps': str(app['_id'])}},
        safe=True,
        )


def generate_grant_code(request, uri, scope, state, app, user):
    code = str(uuid.uuid4())

    parameters = ['code=%s' % code]
    if state:
        parameters.append('state=%s' % state)

    grant = {
        'code': code,
        'scope': scope,
        'client_id': app['client_id'],
        'user': user['_id'],
        }

    request.db.authorization_codes.remove({
            'user': user['_id'],
            'scope': scope,
            'client_id': app['client_id'],
            }, safe=True)
    request.db.authorization_codes.insert(grant, safe=True)

    return '%s?%s' % (uri, '&'.join(parameters))


def find_authorization_code(request, code):
    return request.db.authorization_codes.find_one({'code': code})


def remove_authorization_code(request, grant):
    request.db.authorization_codes.remove(grant, safe=True)


def generate_access_code(request, grant):
    code = str(uuid.uuid4())

    access = {
        'code': code,
        'scope': grant['scope'],
        'user': grant['user'],
        'client_id': grant['client_id'],
        }
    request.db.access_codes.remove({
            'scope': grant['scope'],
            'user': grant['user'],
            'client_id': grant['client_id'],
            }, safe=True)
    request.db.access_codes.insert(access, safe=True)

    return code


def find_access_code(request, code):
    return request.db.access_codes.find_one({'code': code})
