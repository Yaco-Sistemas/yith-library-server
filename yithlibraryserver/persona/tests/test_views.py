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

from mock import patch

from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    def test_persona_login(self):

        res = self.testapp.get('/persona/login', status=405)
        self.assertEqual(res.status, '405 Method Not Allowed')
        res.mustcontain('Only POST is allowed')

        res = self.testapp.post('/persona/login', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('The assertion parameter is required')

        with patch('requests.post') as fake_post:
            fake_post.return_value.ok = False
            res = self.testapp.post('/persona/login', {
                    'assertion': 'test-assertion',
                    'next_url': 'http://localhost/oauth2/clients',
                    }, status=500)
            self.assertEqual(res.status, '500 Internal Server Error')
            res.mustcontain('Mozilla Persona verifier is not working properly')

        with patch('requests.post') as fake_post:
            fake_post.return_value.ok = True
            fake_post.return_value.json = {
                'status': 'failure',
                }
            res = self.testapp.post('/persona/login', {
                    'assertion': 'test-assertion',
                    'next_url': 'http://localhost/oauth2/clients',
                    }, status=403)
            self.assertEqual(res.status, '403 Forbidden')
            res.mustcontain('Mozilla Persona verifier can not verify your identity')

        with patch('requests.post') as fake_post:
            fake_post.return_value.ok = True
            fake_post.return_value.json = {
                'status': 'okay',
                'email': 'john@example.com',
                }
            res = self.testapp.post('/persona/login', {
                    'assertion': 'test-assertion',
                    'next_url': 'http://localhost/oauth2/clients',
                    })
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/register')
