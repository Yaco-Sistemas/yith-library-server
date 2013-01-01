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

from mock import patch

from yithlibraryserver import testing
from yithlibraryserver.compat import urlparse


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_google_login(self):
        res = self.testapp.get('/google/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        self.assertEqual(url.netloc, 'accounts.google.com')
        self.assertEqual(url.path, '/o/oauth2/auth')
        query = urlparse.parse_qs(url.query)
        self.assertEqual(sorted(query.keys()), [
                'client_id', 'redirect_uri', 'response_type', 'scope', 'state',
                ])
        scope = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'

        self.assertEqual(query['scope'], [scope])
        self.assertEqual(query['redirect_uri'],
                         ['http://localhost/google/callback'])
        self.assertEqual(query['client_id'], ['id'])

    def test_google_callback(self):
        # call the login to fill the session
        res = self.testapp.get('/google/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        query = urlparse.parse_qs(url.query)
        state = query['state'][0]

        with patch('requests.post') as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json = {
                'access_token': '1234',
                }
            with patch('requests.get') as fake_get:
                fake_get.return_value.status_code = 200
                fake_get.return_value.json = {
                    'id': '789',
                    'name': 'John Doe',
                    'given_name': 'John',
                    'family_name': 'Doe',
                    'email': 'john@example.com',
                    }

                res = self.testapp.get('/google/callback', {
                    'code': '1234',
                    'state': state,
                    })
                self.assertEqual(res.status, '302 Found')
                self.assertEqual(res.location, 'http://localhost/register')
