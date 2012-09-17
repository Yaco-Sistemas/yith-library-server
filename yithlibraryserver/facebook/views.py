# Yith Library Server is a password storage server.
# Copyright (C) 2012 Yaco Sistemas
# Copyright (C) 2012 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPUnauthorized

import requests

from yithlibraryserver.compat import urlparse, url_encode
from yithlibraryserver.facebook.information import get_user_info
from yithlibraryserver.user.utils import register_or_update


def facebook_login(request):
    settings = request.registry.settings
    redirect_url = request.route_url('facebook_callback')

    state = str(uuid.uuid4())
    request.session['state'] = state

    params = {
        'client_id': settings['facebook_app_id'],
        'redirect_uri': redirect_url,
        'scope': 'email',
        'state': state,
        }

    dialog_url = settings['facebook_dialog_oauth_url']
    url = dialog_url + '?' + url_encode(params)

    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    return HTTPFound(location=url)


def facebook_callback(request):
    settings = request.registry.settings

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
            return HTTPUnauthorized('State parameter does not match internal state. You may be a victim of CSRF')
        else:
            del request.session['state']
    except KeyError:
        return HTTPUnauthorized('Missing internal state. You may be a victim of CSRF')

    params = {
        'client_id': settings['facebook_app_id'],
        'client_secret': settings['facebook_app_secret'],
        'redirect_uri': request.route_url('facebook_callback'),
        'code': code,
        }

    access_token_url = '%s?%s' % (
        settings['facebook_access_token_url'],
        url_encode(params),
        )
    response = requests.get(access_token_url)

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    access_token = response_args['access_token']
    #expires = response_args['expires']

    # get basic information about the user
    info = get_user_info(settings, access_token)
    user_id = info['id']

    return register_or_update(request, 'facebook', user_id, info,
                              request.route_path('home'))
