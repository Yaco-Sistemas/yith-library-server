from mock import patch

from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_twitter_login(self):
        settings = self.testapp.app.registry.settings
        # these are invalid Twitter tokens taken from the examples
        settings['twitter.request_token_url'] = 'https://api.twitter.com/oauth/request_token'
        settings['twitter.consumer_key'] = 'cChZNFj6T5R0TigYB9yd1w'
        settings['twitter.consumer_secret'] = 'L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg'
        settings['twitter.authenticate_url'] = 'https://api.twitter.com/oauth/authenticate'
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
        settings['twitter.request_token_url'] = 'https://api.twitter.com/oauth/request_token'
        settings['twitter.access_token_url'] = 'https://api.twitter.com/oauth/access_token'
        settings['twitter.consumer_key'] = 'cChZNFj6T5R0TigYB9yd1w'
        settings['twitter.consumer_secret'] = 'L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg'
        settings['twitter.authenticate_url'] = 'https://api.twitter.com/oauth/authenticate'

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
            self.assertEqual(res.location, 'http://localhost/register?screen_name=JohnDoe')
            self.assertTrue('Set-Cookie' in res.headers)

        # good request, twitter is happy now. Existing user
        self.db.users.insert({
                'provider_user_id': 'user1',
                'screen_name': 'John Doe',
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
            self.assertEqual(res.location, 'http://localhost/oauth2/applications')
            self.assertTrue('Set-Cookie' in res.headers)
