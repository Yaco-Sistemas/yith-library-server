# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012-2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of Yith Library Server.
#
# Yith Library Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yith Library Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.

import bson
from deform import Button, Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized
from pyramid.view import view_config

from yithlibraryserver.i18n import TranslationString as _
from yithlibraryserver.oauth2.application import create_client_id_and_secret
from yithlibraryserver.oauth2.authentication import authenticate_client
from yithlibraryserver.oauth2.authorization import Authorizator
from yithlibraryserver.oauth2.schemas import ApplicationSchema
from yithlibraryserver.oauth2.schemas import FullApplicationSchema
from yithlibraryserver.user.security import assert_authenticated_user_is_registered


DEFAULT_SCOPE = 'passwords'

SCOPE_NAMES = {
    'passwords': _('Access your passwords'),
    }


@view_config(route_name='oauth2_developer_applications',
             renderer='templates/developer_applications.pt',
             permission='view-applications')
def developer_applications(request):
    assert_authenticated_user_is_registered(request)
    owned_apps_filter = {'owner': request.user['_id']}
    return {
        'applications': request.db.applications.find(owned_apps_filter)
        }


@view_config(route_name='oauth2_developer_application_new',
             renderer='templates/developer_application_new.pt',
             permission='add-application')
def developer_application_new(request):
    assert_authenticated_user_is_registered(request)
    schema = ApplicationSchema()
    button1 = Button('submit', _('Save application'))
    button1.css_class = 'btn-primary'
    button2 = Button('cancel', _('Cancel'))
    button2.css_class = ''
    form = Form(schema, buttons=(button1, button2))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        # the data is fine, save into the db
        application = {
            'owner': request.user['_id'],
            'name': appstruct['name'],
            'main_url': appstruct['main_url'],
            'callback_url': appstruct['callback_url'],
            'production_ready': appstruct['production_ready'],
            'image_url': appstruct['image_url'],
            'description': appstruct['description'],
            }
        create_client_id_and_secret(application)

        request.session.flash(
            _('The application ${app} was created successfully',
              mapping={'app': appstruct['name']}),
            'success')

        request.db.applications.insert(application, safe=True)
        return HTTPFound(
            location=request.route_path('oauth2_developer_applications'))
    elif 'cancel' in request.POST:
        return HTTPFound(
            location=request.route_path('oauth2_developer_applications'))

    # this is a GET
    return {'form': form.render()}


@view_config(route_name='oauth2_developer_application_edit',
             renderer='templates/developer_application_edit.pt',
             permission='edit-application')
def developer_application_edit(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    assert_authenticated_user_is_registered(request)

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    if app['owner'] != request.user['_id']:
        return HTTPUnauthorized()

    schema = FullApplicationSchema()
    button1 = Button('submit', _('Save application'))
    button1.css_class = 'btn-primary'
    button2 = Button('delete', _('Delete application'))
    button2.css_class = 'btn-danger'
    button3 = Button('cancel', _('Cancel'))
    button3.css_class = ''
    form = Form(schema, buttons=(button1, button2, button3))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render(), 'app': app}

        # the data is fine, save into the db
        application = {
            'owner': request.user['_id'],
            'name': appstruct['name'],
            'main_url': appstruct['main_url'],
            'callback_url': appstruct['callback_url'],
            'production_ready': appstruct['production_ready'],
            'image_url': appstruct['image_url'],
            'description': appstruct['description'],
            'client_id': app['client_id'],
            'client_secret': app['client_secret'],
            }

        request.db.applications.update({'_id': app['_id']},
                                       application, safe=True)

        request.session.flash(_('The changes were saved successfully'),
                              'success')

        return HTTPFound(
            location=request.route_path('oauth2_developer_applications'))
    elif 'delete' in request.POST:
        return HTTPFound(
            location=request.route_path('oauth2_developer_application_delete',
                                        app=app['_id']))
    elif 'cancel' in request.POST:
        return HTTPFound(
            location=request.route_path('oauth2_developer_applications'))

    # this is a GET
    return {'form': form.render(app), 'app': app}


@view_config(route_name='oauth2_developer_application_delete',
             renderer='templates/developer_application_delete.pt',
             permission='delete-application')
def developer_application_delete(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    assert_authenticated_user_is_registered(request)
    if app['owner'] != request.user['_id']:
        return HTTPUnauthorized()

    if 'submit' in request.POST:
        request.db.applications.remove(app_id, safe=True)
        request.session.flash(
            _('The application ${app} was deleted successfully',
              mapping={'app': app['name']}),
            'success',
            )
        return HTTPFound(
            location=request.route_path('oauth2_developer_applications'))

    return {'app': app}


@view_config(route_name='oauth2_authorization_endpoint',
             renderer='templates/application_authorization.pt',
             permission='add-authorized-app')
def authorization_endpoint(request):
    response_type = request.params.get('response_type')
    if response_type is None:
        return HTTPBadRequest('Missing required response_type')

    if response_type != 'code':
        return HTTPNotImplemented('Only code is supported')

    client_id = request.params.get('client_id')
    if client_id is None:
        return HTTPBadRequest('Missing required client_type')

    app = request.db.applications.find_one({'client_id': client_id})
    if app is None:
        return HTTPNotFound()

    redirect_uri = request.params.get('redirect_uri')
    if redirect_uri is None:
        redirect_uri = app['callback_url']
    else:
        if redirect_uri != app['callback_url']:
            return HTTPBadRequest(
                'Redirect URI does not match registered callback URL')

    scope = request.params.get('scope', DEFAULT_SCOPE)

    state = request.params.get('state')

    user = assert_authenticated_user_is_registered(request)

    authorizator = Authorizator(request.db, app)

    if 'submit' in request.POST:
        if not authorizator.is_app_authorized(request.user):
            authorizator.store_user_authorization(request.user)

        code = authorizator.auth_codes.create(
            request.user['_id'], app['client_id'], scope)
        url = authorizator.auth_codes.get_redirect_url(
            code, redirect_uri, state)
        return HTTPFound(location=url)

    elif 'cancel' in request.POST:
        return HTTPFound(app['main_url'])

    else:
        if authorizator.is_app_authorized(user):
            code = authorizator.auth_codes.create(
                user['_id'], app['client_id'], scope)
            url = authorizator.auth_codes.get_redirect_url(
                code, redirect_uri, state)
            return HTTPFound(location=url)

        else:
            authorship_information = ''
            owner_id = app.get('owner', None)
            if owner_id is not None:
                owner = request.db.users.find_one({'_id': owner_id})
                if owner:
                    email = owner.get('email', None)
                    if email:
                        authorship_information = _('By ${owner}',
                                                   mapping={'owner': email})

            scopes = [SCOPE_NAMES.get(scope, scope)
                      for scope in scope.split(' ')]
            return {
                'response_type': response_type,
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': scope,
                'state': state,
                'app': app,
                'scopes': scopes,
                'authorship_information': authorship_information,
                }


@view_config(route_name='oauth2_token_endpoint',
             renderer='json')
def token_endpoint(request):
    app = authenticate_client(request)

    grant_type = request.POST.get('grant_type')
    if grant_type is None:
        return HTTPBadRequest('Missing required grant_type')

    if grant_type != 'authorization_code':
        return HTTPNotImplemented('Only authorization_code is supported')

    code = request.POST.get('code')
    if code is None:
        return HTTPBadRequest('Missing required code')

    authorizator = Authorizator(request.db, app)

    grant = authorizator.auth_codes.find(code)
    if grant is None:
        return HTTPUnauthorized()

    # TODO: check if the grant is rotten

    if app['client_id'] != grant['client_id']:
        return HTTPUnauthorized()

    authorizator.auth_codes.remove(grant)

    request.response.headers['Cache-Control'] = 'no-store'
    request.response.headers['Pragma'] = 'no-cache'

    access_code = authorizator.access_codes.create(grant['user'], grant)

    return {
        'access_code': access_code,
        'token_type': 'bearer',
        'expires_in': 3600,
        'scope': grant['scope'],
        }


@view_config(route_name='oauth2_authorized_applications',
             renderer='templates/authorized_applications.pt',
             permission='view-applications')
def authorized_applications(request):
    assert_authenticated_user_is_registered(request)
    authorized_apps_filter = {'_id': {'$in': request.user['authorized_apps']}}
    authorized_apps = request.db.applications.find(authorized_apps_filter)
    return {'authorized_apps': authorized_apps}


@view_config(route_name='oauth2_revoke_application',
             renderer='templates/application_revoke_authorization.pt',
             permission='revoke-authorized-app')
def revoke_application(request):
    assert_authenticated_user_is_registered(request)

    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    authorizator = Authorizator(request.db, app)

    if not authorizator.is_app_authorized(request.user):
        return HTTPUnauthorized()

    if 'submit' in request.POST:
        authorizator.remove_user_authorization(request.user)

        request.session.flash(
            _('The access to application ${app} has been revoked',
              mapping={'app': app['name']}),
            'success',
            )
        return HTTPFound(
            location=request.route_path('oauth2_authorized_applications'))

    return {'app': app}


@view_config(route_name='oauth2_clients',
             renderer='templates/clients.pt')
def clients(request):
    return {'apps': request.db.applications.find({'production_ready': True})}
