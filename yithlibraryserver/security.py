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

from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized
from pyramid.security import Allow, Authenticated


from yithlibraryserver.oauth2.authorization import AccessCodes


class RootFactory(object):

    __acl__ = (
        (Allow, Authenticated, 'user-registration'),
        (Allow, Authenticated, 'view-applications'),
        (Allow, Authenticated, 'edit-application'),
        (Allow, Authenticated, 'add-application'),
        (Allow, Authenticated, 'delete-application'),
        (Allow, Authenticated, 'add-authorized-app'),
        (Allow, Authenticated, 'revoke-authorized-app'),
        (Allow, Authenticated, 'edit-profile'),
        (Allow, Authenticated, 'destroy-account'),
        )

    def __init__(self, request):
        self.request = request


def authorize_user(request):
    authorization = request.headers.get('Authorization')
    if authorization is None:
        raise HTTPUnauthorized()

    method, credentials = request.authorization
    if method.lower() != 'bearer':
        raise HTTPBadRequest('Authorization method not supported')

    access_code = AccessCodes(request.db).find(credentials)
    if access_code is None:
        raise HTTPUnauthorized()

    user_id = access_code['user']
    user = request.db.users.find_one(user_id)
    if user is None:
        raise HTTPUnauthorized()

    return user
