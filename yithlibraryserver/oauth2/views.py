import bson
from deform import Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config

from yithlibraryserver.oauth2.application import create_client_id_and_secret
from yithlibraryserver.oauth2.authentication import authenticate_client
from yithlibraryserver.oauth2.authentication import generate_access_code
from yithlibraryserver.oauth2.authentication import generate_grant_code
from yithlibraryserver.oauth2.authentication import store_user_authorization
from yithlibraryserver.oauth2.authentication import is_app_authorized
from yithlibraryserver.oauth2.schemas import ApplicationSchema


DEFAULT_SCOPE = 'passwords'


@view_config(route_name='oauth2_applications',
             renderer='templates/applications.pt')
def applications(request):
    return {
        'applications': request.db.applications.find()
        }


@view_config(route_name='oauth2_application_new',
             renderer='templates/application_new.pt')
def application_new(request):
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
             renderer='templates/application_view.pt')
def application_view(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    return {'app': app}


@view_config(route_name='oauth2_application_delete',
             renderer='templates/application_delete.pt')
def application_delete(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

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

    user_is_authenticated = True
    user = 'fulanito'

    if user_is_authenticated and is_app_authorized(request, user, app):
        if 'authorization_info' in request.session:
            del request.session['authorization_info']

        url = generate_grant_code(redirect_uri, scope, state)
        return HTTPFound(location=url)
    elif user_is_authenticated:
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
             renderer='templates/application_authorization.pt')
def authorize_application(request):
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

    if 'submit' in request.POST:
        user = 'fulanito'
        store_user_authorization(request, user, app)

        redirect_uri = authorization_info['redirect_uri']
        state = authorization_info['state']
        del request.session['authorization_info']

        url = generate_grant_code(redirect_uri, scope, state)
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

    redirect_uri = request.POST.get('redirect_uri')

    access_code = generate_access_code()

    # headers should be:
    # Cache-Control: no-store
    # Pragma: no-cache
    return {
        'access_code': access_code,
        'token_type': 'bearer',
        'expires_in': 3600,
        'scope': scope,
        }
