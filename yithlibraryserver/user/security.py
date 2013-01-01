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

from pyramid.security import authenticated_userid, unauthenticated_userid
from pyramid.httpexceptions import HTTPFound

from yithlibraryserver.user.models import User


def get_user(request):
    user_id = unauthenticated_userid(request)
    if user_id is None:
        return user_id

    try:
        user = request.db.users.find_one(bson.ObjectId(user_id))
    except bson.errors.InvalidId:
        return None

    return User(user)


def assert_authenticated_user_is_registered(request):
    user_id = authenticated_userid(request)
    try:
        user = request.db.users.find_one(bson.ObjectId(user_id))
    except bson.errors.InvalidId:
        raise HTTPFound(location=request.route_path('register_new_user'))
    else:
        return User(user)
