# Yith Library Server is a password storage server.
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

import hashlib

import requests

from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPServerError

from yithlibraryserver.user.utils import register_or_update


def persona_login(request):
    if request.method != 'POST':
        return HTTPMethodNotAllowed('Only POST is allowed')

    assertion = request.POST.get('assertion', None)
    if assertion is None:
        return HTTPBadRequest('The assertion parameter is required')

    if 'next_url' in request.params and request.params['next_url']:
        request.session['next_url'] = request.params['next_url']

    settings = request.registry.settings
    data = {'assertion': assertion,
            'audience': settings['persona_audience']}
    response = requests.post(settings['persona_verifier_url'],
                             data=data, verify=True)

    if response.ok:
        verification_data = response.json
        if verification_data['status'] == 'okay':
            email = verification_data['email']
            info = {'email': email}
            user_id = hashlib.sha1(email.encode('utf-8')).hexdigest()
            return register_or_update(request, 'persona', user_id,
                                      info, request.route_path('home'))

        else:
            return HTTPForbidden('Mozilla Persona verifier can not verify your identity')
    else:
        return HTTPServerError('Mozilla Persona verifier is not working properly')
