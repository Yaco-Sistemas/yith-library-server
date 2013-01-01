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

import json

import bson

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config, view_defaults

from yithlibraryserver.errors import password_not_found, invalid_password_id
from yithlibraryserver.security import authorize_user
from yithlibraryserver.password.models import PasswordsManager
from yithlibraryserver.password.validation import validate_password


@view_defaults(route_name='password_collection_view', renderer='json')
class PasswordCollectionRESTView(object):

    def __init__(self, request):
        self.request = request
        self.passwords_manager = PasswordsManager(request.db)

    @view_config(request_method='OPTIONS', renderer='string')
    def options(self):
        headers = self.request.response.headers
        headers['Access-Control-Allow-Methods'] = 'GET, POST'
        headers['Access-Control-Allow-Headers'] = ('Origin, Content-Type, '
                                                   'Accept, Authorization')
        return ''

    @view_config(request_method='GET')
    def get(self):
        user = authorize_user(self.request)
        return list(self.passwords_manager.retrieve(user))

    @view_config(request_method='POST')
    def post(self):
        user = authorize_user(self.request)
        password, errors = validate_password(self.request.body,
                                             self.request.charset)

        if errors:
            result = {'message': ','.join(errors)}
            return HTTPBadRequest(body=json.dumps(result),
                                  content_type='application/json')

        return self.passwords_manager.create(user, password)


@view_defaults(route_name='password_view', renderer='json')
class PasswordRESTView(object):

    def __init__(self, request):
        self.request = request
        self.passwords_manager = PasswordsManager(request.db)
        self.password_id = self.request.matchdict['password']

    @view_config(request_method='OPTIONS', renderer='string')
    def options(self):
        headers = self.request.response.headers
        headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE'
        headers['Access-Control-Allow-Headers'] = ('Origin, Content-Type, '
                                                   'Accept, Authorization')
        return ''

    @view_config(request_method='GET')
    def get(self):
        user = authorize_user(self.request)
        try:
            _id = bson.ObjectId(self.password_id)
        except bson.errors.InvalidId:
            return invalid_password_id()

        password = self.passwords_manager.retrieve(user, _id)

        if password is None:
            return password_not_found()
        else:
            return password

    @view_config(request_method='PUT')
    def put(self):
        user = authorize_user(self.request)
        try:
            _id = bson.ObjectId(self.password_id)
        except bson.errors.InvalidId:
            return invalid_password_id()

        password, errors = validate_password(self.request.body,
                                             self.request.charset,
                                             _id)

        if errors:
            result = {'message': ','.join(errors)}
            return HTTPBadRequest(body=json.dumps(result),
                                  content_type='application/json')

        result = self.passwords_manager.update(user, _id, password)
        if result is None:
            return password_not_found()
        else:
            return result

    @view_config(request_method='DELETE')
    def delete(self):
        user = authorize_user(self.request)
        try:
            _id = bson.ObjectId(self.password_id)
        except bson.errors.InvalidId:
            return invalid_password_id()

        if self.passwords_manager.delete(user, _id):
            return ''
        else:
            return password_not_found()
