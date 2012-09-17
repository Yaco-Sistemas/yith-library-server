# Yith Library Server is a password storage server.
# Copyright (C) 2012 Yaco Sistemas
# Copyright (C) 2012 Alejandro Blanco Escudero <korosu.itai@gmail.com>
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
        self.assertEqual(tuple(query.keys()),
                         ('scope', 'state', 'redirect_uri', 'client_id'))
        self.assertEqual(query['scope'], ['email'])
        self.assertEqual(query['redirect_uri'],
                         ['http://localhost/facebook/callback'])
        self.assertEqual(query['client_id'], ['id'])

    def test_facebook_callback(self):
        # bad requests
        res = self.testapp.get('/facebook/callback', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required code')

        res = self.testapp.get('/facebook/callback', {
                'code': '1234',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required state')

        res = self.testapp.get('/facebook/callback', {
                'code': '1234',
                'state': 'mystate',
                }, status=401)
        self.assertEqual(res.status, '401 Unauthorized')
        res.mustcontain('Missing internal state. You may be a victim of CSRF')

        # call the login to fill the session
        res = self.testapp.get('/facebook/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        query = urlparse.parse_qs(url.query)
        state = query['state'][0]

        res = self.testapp.get('/facebook/callback', {
                'code': '1234',
                'state': 'mystate',
                }, status=401)
        self.assertEqual(res.status, '401 Unauthorized')
        res.mustcontain('State parameter does not match internal state. You may be a victim of CSRF')

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 401
            response.text = 'Facebook does not want us'
            res = self.testapp.get('/facebook/callback', {
                    'code': '1234',
                    'state': state,
                    }, status=401)
            self.assertEqual(res.status, '401 Unauthorized')
            res.mustcontain('Facebook does not want us')

        res = self.testapp.get('/facebook/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        query = urlparse.parse_qs(url.query)
        state = query['state'][0]

        with patch('requests.get') as fake:
            # simulate different return values
            def side_effect(*args):

                def second_call(*args):
                    fake.return_value.status_code = 200
                    fake.return_value.json = {
                        'id': '789',
                        'username': 'john.doe',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'john@example.com',
                        }
                    return fake.return_value

                fake.return_value.status_code = 200
                fake.return_value.text = 'access_token=xyz&expires=1000'
                fake.side_effect = second_call
                return fake.return_value
            fake.side_effect  = side_effect

            res = self.testapp.get('/facebook/callback', {
                    'code': '1234',
                    'state': state,
                    })
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/register')

        # do the same login but with an existing user
        self.db.users.insert({
                'facebook_id': '789',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                }, safe=True)

        res = self.testapp.get('/facebook/login', {
                'next_url': 'https://localhost/foo/bar',
                })
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        query = urlparse.parse_qs(url.query)
        state = query['state'][0]

        with patch('requests.get') as fake:
            # simulate different return values
            def side_effect2(*args):

                def second_call2(*args):
                    fake.return_value.status_code = 200
                    fake.return_value.json = {
                        'id': '789',
                        'username': 'john.doe',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'john@example.com',
                        }
                    return fake.return_value

                fake.return_value.status_code = 200
                fake.return_value.text = 'access_token=xyz&expires=1000'
                fake.side_effect = second_call2
                return fake.return_value
            fake.side_effect  = side_effect2

            res = self.testapp.get('/facebook/callback', {
                    'code': '1234',
                    'state': state,
                    })
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'https://localhost/foo/bar')
            self.assertTrue('Set-Cookie' in res.headers)

        # and the same thing without setting a next_url in the login view
        res = self.testapp.get('/facebook/login')
        self.assertEqual(res.status, '302 Found')
        url = urlparse.urlparse(res.location)
        query = urlparse.parse_qs(url.query)
        state = query['state'][0]

        with patch('requests.get') as fake:
            # simulate different return values
            def side_effect3(*args):

                def second_call3(*args):
                    fake.return_value.status_code = 200
                    fake.return_value.json = {
                        'id': '789',
                        'username': 'john.doe',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'john@example.com',
                        }
                    return fake.return_value

                fake.return_value.status_code = 200
                fake.return_value.text = 'access_token=xyz&expires=1000'
                fake.side_effect = second_call3
                return fake.return_value
            fake.side_effect  = side_effect3

            res = self.testapp.get('/facebook/callback', {
                    'code': '1234',
                    'state': state,
                    })
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/')
            self.assertTrue('Set-Cookie' in res.headers)
