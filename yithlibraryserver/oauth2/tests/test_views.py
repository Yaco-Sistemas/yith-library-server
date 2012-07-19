import bson

from yithlibraryserver import testing
from yithlibraryserver.oauth2.views import DEFAULT_SCOPE
from yithlibraryserver.oauth2.authentication import auth_basic_encode


class ViewTests(testing.TestCase):

    clean_collections = ('applications', 'users', 'authorization_codes',
                         'access_codes')

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
                'screen_name': 'John Doe',
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
            'Authorization': auth_basic_encode('123456', 'secret'),
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
                'screen_name': 'John Doe',
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
                'screen_name': 'John Doe',
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
            'Authorization': auth_basic_encode('98765', 'secret2'),
            }
        res = self.testapp.post('/oauth2/endpoints/token', {
                'grant_type': 'authorization_code',
                'code': code,
                }, headers=headers, status=401)
        self.assertEqual(res.status, '401 Unauthorized')

    def test_authenticate_anonymous(self):
        # there is nothing in the session yet
        res = self.testapp.get('/oauth2/authenticate_anonymous/123456',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')

        # ask for authorization first, so it is stored in the session
        app_id = self.db.applications.insert({
                'client_id': '123456',
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'https://example.com/callback',
                }, safe=True)
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })

        # invalid app id
        res = self.testapp.get('/oauth2/authenticate_anonymous/xx',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        # non existing app id
        res = self.testapp.get('/oauth2/authenticate_anonymous/000000000000000000000000',
                               status=404)
        self.assertEqual(res.status, '404 Not Found')

        # valid app id
        res = self.testapp.get('/oauth2/authenticate_anonymous/%s' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Authorize application Test Application')
        res.mustcontain('You need to log in first')

    def test_authorize_application(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/authorizeapp/123456')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'screen_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        # there is nothing in the session yet
        res = self.testapp.get('/oauth2/authorizeapp/123456',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')

        # ask for authorization first, so it is stored in the session
        app_id = self.db.applications.insert({
                'client_id': '123456',
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'https://example.com/callback',
                }, safe=True)
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                })

        # invalid app id
        res = self.testapp.get('/oauth2/authorizeapp/xx',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        # non existing app id
        res = self.testapp.get('/oauth2/authorizeapp/000000000000000000000000',
                               status=404)
        self.assertEqual(res.status, '404 Not Found')

        # valid app id
        valid_url = '/oauth2/authorizeapp/%s' % str(app_id)
        res = self.testapp.get(valid_url)
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Authorize application Test Application')
        res.mustcontain('Do you want to allow this access?')
        res.mustcontain('Yes, I authorize the Test Application application')
        res.mustcontain('You can revoke this permission in the future.')

        # do the post
        res = self.testapp.post(valid_url, {
                'submit': 'Yes, I authorize the Test Application application',
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

    def test_applications(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'screen_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('John Doe')
        res.mustcontain('Log out')
        res.mustcontain('Authorized Applications')
        res.mustcontain('Developer Applications')
        res.mustcontain('Register new application')

        # TODO: test creating apps and make sure they appear in the output

    def test_application_new(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'screen_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('New Application')
        res.mustcontain('Name')
        res.mustcontain('Main Url')
        res.mustcontain('Callback Url')


        res = self.testapp.post('/oauth2/applications/new', {
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'http://example.com/callback',
                'submit': 'submit',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/applications')

        app = self.db.applications.find_one({
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'http://example.com/callback',
                })
        self.assertNotEqual(app, None)
        self.assertTrue('client_id' in app)
        self.assertTrue('client_secret' in app)
        self.assertEqual(app['owner'], user_id)
        self.assertEqual(app['name'], 'Test Application')
        self.assertEqual(app['main_url'], 'http://example.com')
        self.assertEqual(app['callback_url'], 'http://example.com/callback')

        # error if we don't fill all fields
        res = self.testapp.post('/oauth2/applications/new', {
                'name': 'Test Application',
                'callback_url': 'http://example.com/callback',
                'submit': 'submit',
                })
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('There was a problem with your submission')

    def test_application_delete(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'screen_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/xxx/delete',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        res = self.testapp.get('/oauth2/applications/000000000000000000000000/delete',
                               status=404)
        self.assertEqual(res.status, '404 Not Found')

        # create a valid app
        app_id = self.db.applications.insert({
                'owner': bson.ObjectId(),
                'name': 'Test Application',
                'client_id': '123456',
                'callback_url': 'https://example.com/callback',
                }, safe=True)

        res = self.testapp.get('/oauth2/applications/%s/delete' % str(app_id),
                               status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        self.db.applications.update({'_id': app_id}, {
                '$set': {'owner': user_id},
                }, safe=True)
        res = self.testapp.get('/oauth2/applications/%s/delete' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Delete Application Test Application')
        res.mustcontain('Are you sure you want to remove the application')
        res.mustcontain('Yes, I am sure')
        res.mustcontain('No, take me back to the application list')

        # now delete it
        res = self.testapp.post('/oauth2/applications/%s/delete' % str(app_id),
                                {'submit': 'Yes, I am sure'})
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/applications')

        app = self.db.applications.find_one(app_id)
        self.assertEqual(app, None)

    def test_application_view(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'screen_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/xxx',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        res = self.testapp.get('/oauth2/applications/000000000000000000000000',
                               status=404)
        self.assertEqual(res.status, '404 Not Found')

        # create a valid app
        app_id = self.db.applications.insert({
                'owner': bson.ObjectId(),
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'http://example.com/callback',
                'client_id': '123456',
                'client_secret': 'secret',
                }, safe=True)

        res = self.testapp.get('/oauth2/applications/%s' % str(app_id),
                               status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        self.db.applications.update({'_id': app_id}, {
                '$set': {'owner': user_id},
                }, safe=True)
        res = self.testapp.get('/oauth2/applications/%s' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('View Application')
        res.mustcontain('Application Test Application')
        res.mustcontain('Id:')
        res.mustcontain(str(app_id))
        res.mustcontain('Name:')
        res.mustcontain('Test Application')
        res.mustcontain('Main URL:')
        res.mustcontain('http://example.com')
        res.mustcontain('Callback URL:')
        res.mustcontain('http://example.com/callback')
        res.mustcontain('Client Id:')
        res.mustcontain('123456')
        res.mustcontain('Client Secret:')
        res.mustcontain('secret')
        res.mustcontain('Delete application')
        res.mustcontain('Back to the application list')
