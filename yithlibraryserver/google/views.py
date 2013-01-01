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

from yithlibraryserver.oauth2.client import get_user_info
from yithlibraryserver.oauth2.client import oauth2_step1, oauth2_step2
from yithlibraryserver.user.utils import register_or_update


def _get_scope():
    return ' '.join([
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                ])


def google_login(request):
    settings = request.registry.settings
    return oauth2_step1(
        request=request,
        auth_uri=settings['google_auth_uri'],
        client_id=settings['google_client_id'],
        redirect_url=request.route_url('google_callback'),
        scope=_get_scope(),
        )


def google_callback(request):
    settings = request.registry.settings
    access_token = oauth2_step2(
        request=request,
        token_uri=settings['google_token_uri'],
        client_id=settings['google_client_id'],
        client_secret=settings['google_client_secret'],
        redirect_url=request.route_url('google_callback'),
        scope=_get_scope(),
       )

    info = get_user_info(settings['google_user_info_uri'], access_token)
    user_id = info['id']
    new_info = {
        'screen_name': info.get('name', ''),
        'first_name': info.get('given_name', ''),
        'last_name': info.get('family_name', ''),
        'email': info.get('email', ''),
        }

    return register_or_update(request, 'google', user_id, new_info,
                              request.route_path('home'))
