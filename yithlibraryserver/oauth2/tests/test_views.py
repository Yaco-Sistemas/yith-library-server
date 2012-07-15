from pyramid.security import remember

from webtest import TestRequest

from yithlibraryserver import testing
from yithlibraryserver.oauth2.views import DEFAULT_SCOPE


class ViewTests(testing.ViewTests):

    def tearDown(self):
        super(ViewTests, self).tearDown()
        self.db.drop_collection('applications')
        self.db.drop_collection('users')

    def set_user_cookie(self, userid):
        request = TestRequest.blank('', {})
        request.registry = self.testapp.app.registry
        remember_headers = remember(request, userid)
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
        userid = self.db.users.insert({
                'provider_user_id': 'twitter1',
                'scree_name': 'John Doe',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(userid))

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
            {'_id': userid},
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
                'user': userid,
                })
        self.assertNotEqual(grant, None)
        code = grant['code']
        location = 'https://example.com/callback?code=%s' % code
        self.assertEqual(res.location, location)
