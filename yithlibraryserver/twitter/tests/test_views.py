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


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_twitter_login(self):
        settings = self.testapp.app.registry.settings
        # these are invalid Twitter tokens taken from the examples
        settings['twitter_request_token_url'] = 'https://api.twitter.com/oauth/request_token'
        settings['twitter_consumer_key'] = 'cChZNFj6T5R0TigYB9yd1w'
        settings['twitter_consumer_secret'] = 'L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg'
        settings['twitter_authenticate_url'] = 'https://api.twitter.com/oauth/authenticate'
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            res = self.testapp.get('/twitter/login')
            self.assertEqual(res.status, '302 Found')
            loc = 'https://api.twitter.com/oauth/authenticate?oauth_token=123456789'
            self.assertEqual(res.location, loc)

        # simulate an authentication error from Twitter
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 401
            res = self.testapp.get('/twitter/login', status=401)
            self.assertEqual(res.status, '401 Unauthorized')

        # simulate an oauth_callback_confirmed=false
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=false'
            res = self.testapp.get('/twitter/login', status=401)
            self.assertEqual(res.status, '401 Unauthorized')
            res.mustcontain('oauth_callback_confirmed is not true')

    def test_twitter_callback(self):
        settings = self.testapp.app.registry.settings
        settings['twitter_request_token_url'] = 'https://api.twitter.com/oauth/request_token'
        settings['twitter_access_token_url'] = 'https://api.twitter.com/oauth/access_token'
        settings['twitter_consumer_key'] = 'cChZNFj6T5R0TigYB9yd1w'
        settings['twitter_consumer_secret'] = 'L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg'
        settings['twitter_authenticate_url'] = 'https://api.twitter.com/oauth/authenticate'

        res = self.testapp.get('/twitter/callback', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required oauth_token')

        res = self.testapp.get('/twitter/callback?oauth_token=123456789',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required oauth_verifier')

        good_url = '/twitter/callback?oauth_token=123456789&oauth_verifier=abc'
        res = self.testapp.get(good_url, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('No oauth_token was found in the session')

        # bad request because oauth tokens are different
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=987654321'
            self.testapp.get('/twitter/login')

            res = self.testapp.get(good_url, status=401)
            self.assertEqual(res.status, '401 Unauthorized')
            res.mustcontain("OAuth tokens don't match")

        # good request, twitter is not happy with us
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            self.testapp.get('/twitter/login')

            response = fake.return_value
            response.status_code = 401
            response.text = 'Invalid token'

            res = self.testapp.get(good_url, status=401)
            self.assertEqual(res.status, '401 Unauthorized')
            res.mustcontain('Invalid token')

        # good request, twitter is happy now. New user
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            self.testapp.get('/twitter/login')

            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_token=xyz&user_id=user1&screen_name=JohnDoe'

            with patch('requests.get') as fake2:
                response2 = fake2.return_value
                response2.status_code = 200
                response2.json = {'name': 'John Doe'}

                res = self.testapp.get(good_url, status=302)
                self.assertEqual(res.status, '302 Found')
                self.assertEqual(res.location, 'http://localhost/register')

        # good request, twitter is happy now. Existing user
        user_id = self.db.users.insert({
                'twitter_id': 'user1',
                'screen_name': 'Johnny',
                }, safe=True)
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            self.testapp.get('/twitter/login')

            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_token=xyz&user_id=user1&screen_name=JohnDoe'

            with patch('requests.get') as fake2:
                response2 = fake2.return_value
                response2.status_code = 200
                response2.json = {'name': 'John Doe'}

                res = self.testapp.get(good_url, status=302)
                self.assertEqual(res.status, '302 Found')
                self.assertEqual(res.location, 'http://localhost/')
                self.assertTrue('Set-Cookie' in res.headers)

                # even if the response from twitter included a different
                # screen_name, our user will not be updated
                new_user = self.db.users.find_one({'_id': user_id}, safe=True)
                self.assertEqual(new_user['screen_name'], 'Johnny')

        # good request, existing user, remember next_url
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            self.testapp.get('/twitter/login?next_url=http://localhost/foo/bar')

            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_token=xyz&user_id=user1&screen_name=JohnDoe'

            with patch('requests.get') as fake2:
                response2 = fake2.return_value
                response2.status_code = 200
                response2.json = {'name': 'John Doe'}

                res = self.testapp.get(good_url, status=302)
                self.assertEqual(res.status, '302 Found')
                self.assertEqual(res.location, 'http://localhost/foo/bar')
                self.assertTrue('Set-Cookie' in res.headers)
