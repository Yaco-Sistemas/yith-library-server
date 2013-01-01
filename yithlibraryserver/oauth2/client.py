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

import uuid

import requests

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPUnauthorized

from yithlibraryserver.compat import urlparse, url_encode


def oauth2_step1(request, auth_uri, client_id, redirect_url, scope):
    state = str(uuid.uuid4())
    request.session['state'] = state

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_url,
        'scope': scope,
        'state': state,
        }

    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    return HTTPFound(location=auth_uri + '?' + url_encode(params))


def oauth2_step2(request, token_uri, client_id, client_secret, redirect_url,
                 scope):
    try:
        code = request.params['code']
    except KeyError:
        return HTTPBadRequest('Missing required code')

    try:
        state = request.params['state']
    except KeyError:
        return HTTPBadRequest('Missing required state')

    try:
        my_state = request.session['state']
        if state != my_state:
            return HTTPUnauthorized('State parameter does not match internal '
                                    'state. You may be a victim of CSRF')
        else:
            del request.session['state']
    except KeyError:
        return HTTPUnauthorized('Missing internal state. '
                                'You may be a victim of CSRF')

    params = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_url,
        'scope': scope,
        }

    response = requests.post(token_uri, data=params)

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    if response.json is None:
        response_json = dict(urlparse.parse_qsl(response.text))
    else:
        response_json = response.json

    return response_json['access_token']


def get_user_info(info_uri, access_token):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        }

    response = requests.get(info_uri, headers=headers)

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    return response.json
