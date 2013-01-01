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

import requests

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.compat import url_encode
from yithlibraryserver.twitter.authorization import auth_header


def get_user_info(settings, user_id, oauth_token):
    user_info_url = settings['twitter_user_info_url']

    params = (
        ('oauth_token', oauth_token),
        )

    auth = auth_header('GET', user_info_url, params, settings, oauth_token)

    response = requests.get(
        user_info_url + '?' + url_encode({'user_id': user_id}),
        headers={'Authorization': auth},
        )

    if response.status_code != 200:
        raise HTTPUnauthorized(response.text)

    return response.json
