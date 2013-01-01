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

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPUnauthorized

import requests

from yithlibraryserver.compat import urlparse
from yithlibraryserver.twitter.authorization import auth_header
from yithlibraryserver.twitter.information import get_user_info
from yithlibraryserver.user.utils import split_name, register_or_update
from yithlibraryserver.user.utils import user_from_provider_id


def twitter_login(request):
    settings = request.registry.settings
    request_token_url = settings['twitter_request_token_url']
    oauth_callback_url = request.route_url('twitter_callback')

    params = (
        ('oauth_callback', oauth_callback_url),
        )

    auth = auth_header('POST', request_token_url, params, settings)

    response = requests.post(request_token_url, data='',
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    if response_args['oauth_callback_confirmed'] != 'true':
        return HTTPUnauthorized('oauth_callback_confirmed is not true')

    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    request.session['oauth_token'] = oauth_token
    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    authorize_url = '%s?oauth_token=%s' % (
        settings['twitter_authenticate_url'], oauth_token
        )
    return HTTPFound(location=authorize_url)


def twitter_callback(request):
    settings = request.registry.settings

    try:
        oauth_token = request.params['oauth_token']
    except KeyError:
        return HTTPBadRequest('Missing required oauth_token')

    try:
        oauth_verifier = request.params['oauth_verifier']
    except KeyError:
        return HTTPBadRequest('Missing required oauth_verifier')

    try:
        saved_oauth_token = request.session['oauth_token']
    except KeyError:
        return HTTPBadRequest('No oauth_token was found in the session')

    if saved_oauth_token != oauth_token:
        return HTTPUnauthorized("OAuth tokens don't match")
    else:
        del request.session['oauth_token']

    access_token_url = settings['twitter_access_token_url']

    params = (
        ('oauth_token', oauth_token),
        )

    auth = auth_header('POST', access_token_url, params, settings, oauth_token)

    response = requests.post(access_token_url,
                             data='oauth_verifier=%s' % oauth_verifier,
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    user_id = response_args['user_id']
    screen_name = response_args['screen_name']

    existing_user = user_from_provider_id(request.db, 'twitter', user_id)
    if existing_user is None:
        # fetch Twitter info only if this is the first time for
        # the user sice Twitter has very strong limits for using
        # its APIs
        twitter_info = get_user_info(settings, user_id, oauth_token)
        first_name, last_name = split_name(twitter_info['name'])
        info = {
            'screen_name': screen_name,
            'first_name': first_name,
            'last_name': last_name,
            }
    else:
        info = {}

    return register_or_update(request, 'twitter', user_id, info,
                              request.route_path('home'))
