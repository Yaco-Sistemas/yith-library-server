import bson
from deform import Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized
from pyramid.view import view_config

from yithlibraryserver.oauth2.application import create_client_id_and_secret
from yithlibraryserver.oauth2.authentication import authenticate_client
from yithlibraryserver.oauth2.authentication import generate_access_code
from yithlibraryserver.oauth2.authentication import generate_grant_code
from yithlibraryserver.oauth2.authentication import store_user_authorization
from yithlibraryserver.oauth2.authentication import is_app_authorized
from yithlibraryserver.oauth2.authentication import find_authorization_code
from yithlibraryserver.oauth2.authentication import remove_authorization_code
from yithlibraryserver.oauth2.schemas import ApplicationSchema
from yithlibraryserver.user import get_authenticated_user


DEFAULT_SCOPE = 'passwords'


@view_config(route_name='oauth2_applications',
             renderer='templates/applications.pt',
             permission='view-applications')
def applications(request):
    user = get_authenticated_user(request)
    return {
        'screen_name': user['screen_name'],
        'authorized_apps': [str(app) for app in user['authorized_apps']],
        'applications': request.db.applications.find({'owner': user['_id']})
        }


@view_config(route_name='oauth2_application_new',
             renderer='templates/application_new.pt',
             permission='add-application')
def application_new(request):
    user = get_authenticated_user(request)
    schema = ApplicationSchema()
    form = Form(schema, buttons=('submit', ))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        # the data is fine, save into the db
        application = {
            'owner': user['_id'],
            'name': appstruct['name'],
            'main_url': appstruct['main_url'],
            'callback_url': appstruct['callback_url'],
            }
        create_client_id_and_secret(application)

        request.db.applications.insert(application, safe=True)
        return HTTPFound(location=request.route_url('oauth2_applications'))

    # this is a GET
    return {'form': form.render()}


@view_config(route_name='oauth2_application_view',
             renderer='templates/application_view.pt',
             permission='view-application')
def application_view(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    user = get_authenticated_user(request)

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    if app['owner'] != user['_id']:
        return HTTPUnauthorized()

    return {'app': app}


@view_config(route_name='oauth2_application_delete',
             renderer='templates/application_delete.pt',
             permission='delete-application')
def application_delete(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    user = get_authenticated_user(request)
    if app['owner'] != user['_id']:
        return HTTPUnauthorized()

    if 'submit' in request.POST:
        request.db.applications.remove(app_id, safe=True)
        return HTTPFound(location=request.route_url('oauth2_applications'))

    return {'app': app}


@view_config(route_name='oauth2_authorization_endpoint',
             renderer='string')
def authorization_endpoint(request):
    response_type = request.params.get('response_type')
    if response_type is None:
        return HTTPBadRequest('Missing required response_ẗype')

    if response_type != 'code':
        return HTTPNotImplemented('Only code is supported')

    # code grant
    client_id = request.params.get('client_id')
    if client_id is None:
        return HTTPBadRequest('Missing required client_ẗype')

    app = request.db.applications.find_one({'client_id': client_id})
    if app is None:
        return HTTPNotFound()

    redirect_uri = request.params.get('redirect_uri')
    if redirect_uri is None:
        redirect_uri = app['callback_url']
    else:
        if redirect_uri != app['callback_url']:
            return HTTPBadRequest('Redirect URI does not match registered callback URL')

    scope = request.params.get('scope', DEFAULT_SCOPE)

    state = request.params.get('state')

    user = get_authenticated_user(request)

    if user and is_app_authorized(request, user, app):
        if 'authorization_info' in request.session:
            del request.session['authorization_info']

        url = generate_grant_code(request, redirect_uri, scope, state, app, user)
        return HTTPFound(location=url)
    elif user:
        request.session['authorization_info'] = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state
            }
        return HTTPFound(request.route_url('oauth2_authorize_application', app=str(app['_id'])))
    else:
        request.session['authorization_info'] = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state
            }
        return HTTPFound(request.route_url('oauth2_authenticate_anonymous', app=str(app['_id'])))


@view_config(route_name='oauth2_authorize_application',
             renderer='templates/application_authorization.pt',
             permission='add-authorized-app')
def authorize_application(request):
    try:
        authorization_info = request.session['authorization_info']
    except KeyError:
        return HTTPBadRequest()

    user = get_authenticated_user(request)

    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    scope = authorization_info['scope']

    if 'submit' in request.POST:
        store_user_authorization(request, user, app)

        redirect_uri = authorization_info['redirect_uri']
        state = authorization_info['state']
        del request.session['authorization_info']

        url = generate_grant_code(request, redirect_uri, scope, state, app, user)
        return HTTPFound(location=url)

    return {'app': app, 'scopes': scope.split(' ')}


@view_config(route_name='oauth2_authenticate_anonymous',
             renderer='templates/authenticate_anonymous.pt')
def authenticate_anonymous(request):
    try:
        authorization_info = request.session['authorization_info']
    except KeyError:
        return HTTPBadRequest()

    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    scope = authorization_info['scope']

    return {'app': app, 'scopes': scope.split(' ')}


@view_config(route_name='oauth2_token_endpoint',
             renderer='json')
def token_endpoint(request):
    app = authenticate_client(request)

    grant_type = request.POST.get('grant_type')
    if grant_type is None:
        return HTTPBadRequest('Missing required grant_ẗype')

    if grant_type != 'authorization_code':
        return HTTPNotImplemented('Only authorization_code is supported')

    code = request.POST.get('code')
    if code is None:
        return HTTPBadRequest('Missing required code')

    grant = find_authorization_code(request, code)
    if grant is None:
        return HTTPUnauthorized()

    # TODO: check if the grant is rotten

    if app['client_id'] != grant['client_id']:
        return HTTPUnauthorized()

    remove_authorization_code(request, grant)
    access_code = generate_access_code(request, grant)

    request.response.headers['Cache-Control'] = 'no-store'
    request.response.headers['Pragma'] = 'no-cache'
    return {
        'access_code': access_code,
        'token_type': 'bearer',
        'expires_in': 3600,
        'scope': grant['scope'],
        }
