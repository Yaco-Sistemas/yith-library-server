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

            res = self.testapp.get(good_url, status=302)
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/register?next_url=http%3A%2F%2Flocalhost%2F&screen_name=JohnDoe')
            self.assertTrue('Set-Cookie' in res.headers)

        # good request, twitter is happy now. Existing user
        user_id = self.db.users.insert({
                'provider_user_id': 'user1',
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

            res = self.testapp.get(good_url, status=302)
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/')
            self.assertTrue('Set-Cookie' in res.headers)

            # as the response from twitter included a different
            # screen_name, our user must be updated
            new_user = self.db.users.find_one({'_id': user_id}, safe=True)
            self.assertEqual(new_user['screen_name'], 'JohnDoe')

        # good request, existing user, remember next_url
        with patch('requests.post') as fake:
            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_callback_confirmed=true&oauth_token=123456789'
            self.testapp.get('/twitter/login?next_url=http://localhost/foo/bar')

            response = fake.return_value
            response.status_code = 200
            response.text = 'oauth_token=xyz&user_id=user1&screen_name=JohnDoe'

            res = self.testapp.get(good_url, status=302)
            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'http://localhost/foo/bar')
            self.assertTrue('Set-Cookie' in res.headers)
