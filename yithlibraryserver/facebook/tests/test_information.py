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

import unittest
from mock import patch

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.facebook.information import get_user_info


class InformationTests(unittest.TestCase):

    def test_get_user_info(self):
        settings = {
            'facebook_app_id': 'id',
            'facebook_secret': 'secret',
            'facebook_basic_information_url': 'https://graph.facebook.com/me'
            }

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 200
            response.json = {'first_name': 'John',
                             'last_name': 'Doe',
                             'email': 'john@example.com'}

            info = get_user_info(settings, 'token')
            self.assertEqual(info, {'first_name': 'John',
                                    'last_name': 'Doe',
                                    'email': 'john@example.com'})

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 400
            response.json = {}

            self.assertRaises(HTTPUnauthorized,
                              get_user_info, settings, 'token')
