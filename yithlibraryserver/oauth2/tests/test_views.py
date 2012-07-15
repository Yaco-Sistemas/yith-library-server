import base64

from pyramid.security import remember

from webtest import TestRequest

from yithlibraryserver import testing
from yithlibraryserver.oauth2.views import DEFAULT_SCOPE


def auth_basic_encode(user, password):
    value = '%s:%s' % (user, password)
    return base64.encodebytes(value.encode('utf-8')).decode('ascii')


class ViewTests(testing.ViewTests):

    def tearDown(self):
        super(ViewTests, self).tearDown()
        self.db.drop_collection('applications')
        self.db.drop_collection('users')
        self.db.drop_collection('authorization_codes')
        self.db.drop_collection('access_codes')

        self.testapp.reset()

    def set_user_cookie(self, user_id):
        request = TestRequest.blank('', {})
        request.registry = self.testapp.app.registry
        remember_headers = remember(request, user_id)
        cookie_value = remember_headers[0][1].split('"')[1]
        self.testapp.cookies['auth_tkt'] = cookie_value

    def test_authorization_endpoint(self):
        # 1. test incorrect requests
        res = self.testapp.get('/oauth2/endpoints/authorization',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required response_type')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'token',
                }, status=501)

        self.assertEqual(res.status, '501 Not Implemented')
        res.mustcontain('Only code is supported')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required client_type')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '1234',
                }, status=404)
        self.assertEqual(res.status, '404 Not Found')

        # create a valid app
        app_id = self.db.applications.insert({
                'client_id': '123456',
                'callback_url': 'https://example.com/callback',
                }, safe=True)

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/bad-callback',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Redirect URI does not match registered callback URL')

        # 2. Valid requests
        # anonymous user
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        location = 'http://localhost/oauth2/authenticate_anonymous/%s' % app_id
        self.assertEqual(res.location, location)

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                # redirect_uri is optional
                })
        self.assertEqual(res.status, '302 Found')
        location = 'http://localhost/oauth2/authenticate_anonymous/%s' % app_id
        self.assertEqual(res.location, location)

        # authenticated user who hasn't authorized the app
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'scree_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        location = 'http://localhost/oauth2/authorizeapp/%s' % app_id
        self.assertEqual(res.location, location)

        # authenticated user who has authorized the app
        self.db.users.update(
            {'_id': user_id},
            {'$addToSet': {'authorized_apps': app_id}},
            safe=True,
            )

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        self.assertNotEqual(grant, None)
        code = grant['code']
        location = 'https://example.com/callback?code=%s' % code
        self.assertEqual(res.location, location)

    def test_token_endpoint(self):
        # 1. test incorrect requests
        res = self.testapp.post('/oauth2/endpoints/token', {}, status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        headers = {
            'Authorization': 'Basic ' + auth_basic_encode('123456', 'secret'),
            }

        res = self.testapp.post('/oauth2/endpoints/token', {}, headers=headers, status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        app_id = self.db.applications.insert({
                'client_id': '123456',
                'client_secret': 'secret',
                'callback_url': 'https://example.com/callback',
                }, safe=True)

        res = self.testapp.post('/oauth2/endpoints/token', {}, headers=headers, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required grant_type')

        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'password'
                }, headers=headers, status=501)
        self.assertEqual(res.status, '501 Not Implemented')
        res.mustcontain('Only authorization_code is supported')

        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'authorization_code',
                }, headers=headers, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required code')

        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'authorization_code',
                'code': 'this-code-does-not-exist',
                }, headers=headers, status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        # 2. Test a valid request

        # first we generate an authorization_code
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'scree_name': 'John Doe',
                'authorized_apps': [app_id],
                }, safe=True)
        self.set_user_cookie(str(user_id))
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        self.assertNotEqual(grant, None)
        code = grant['code']

        # now send the token request
        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'authorization_code',
                'code': code,
                }, headers=headers)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.headers['Cache-Control'], 'no-store')
        self.assertEqual(res.headers['Pragma'], 'no-cache')

        # the grant code should be removed
        grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        self.assertEqual(grant, None)

        # and an access token should be created
        self.assertEqual(res.json['token_type'], 'bearer')
        self.assertEqual(res.json['expires_in'], 3600)
        self.assertEqual(res.json['scope'], DEFAULT_SCOPE)

        access_code = self.db.access_codes.find_one({
                'code': res.json['access_code'],
                })
        self.assertNotEqual(access_code, None)

    def test_token_endpoint_bad_client_id(self):
        app_id = self.db.applications.insert({
                'client_id': '123456',
                'client_secret': 'secret',
                'callback_url': 'https://example.com/callback',
                }, safe=True)

        app_id2 = self.db.applications.insert({
                'client_id': '98765',
                'client_secret': 'secret2',
                'callback_url': 'https://example.com/callback2',
                }, safe=True)

        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'scree_name': 'John Doe',
                'authorized_apps': [app_id, app_id2],
                }, safe=True)
        self.set_user_cookie(str(user_id))
        self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                })
        grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        code = grant['code']

        # Authorize with app2 credentials
        headers = {
            'Authorization': 'Basic ' + auth_basic_encode('98765', 'secret2'),
            }
        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'authorization_code',
                'code': code,
                }, headers=headers, status=401)
        self.assertEqual(res.status, '401 Unauthorized')
