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

from mock import patch

from yithlibraryserver import testing
from yithlibraryserver.compat import urlparse


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_facebook_login(self):
        res = self.testapp.get('/facebook/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        self.assertEqual(url.netloc, 'www.facebook.com')
        self.assertEqual(url.path, '/dialog/oauth/')
        query = urlparse.parse_qs(url.query)
        self.assertEqual(sorted(query.keys()), [
                'client_id', 'redirect_uri', 'response_type', 'scope', 'state',
                ])
        self.assertEqual(query['scope'], ['email'])
        self.assertEqual(query['redirect_uri'],
                         ['http://localhost/facebook/callback'])
        self.assertEqual(query['client_id'], ['id'])

    def test_facebook_callback(self):
        # call the login to fill the session
        res = self.testapp.get('/facebook/login', {
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
                    'username': 'john.doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    }

                res = self.testapp.get('/facebook/callback', {
                    'code': '1234',
                    'state': state,
                    })
                self.assertEqual(res.status, '302 Found')
                self.assertEqual(res.location, 'http://localhost/register')
