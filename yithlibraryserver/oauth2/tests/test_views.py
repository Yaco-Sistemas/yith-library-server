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

import bson

from yithlibraryserver import testing
from yithlibraryserver.oauth2.views import DEFAULT_SCOPE
from yithlibraryserver.oauth2.authentication import auth_basic_encode


class ViewTests(testing.TestCase):

    clean_collections = ('applications', 'users', 'authorization_codes',
                         'access_codes')

    def test_authorization_endpoint(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/endpoints/authorization')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

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
        owner_id = self.db.users.insert({
                'twitter_id': 'twitter2',
                'screen_name': 'Administrator',
                'first_name': 'Alice',
                'last_name': 'Doe',
                'email': 'alice@example.com',
                'authorized_apps': [],
                }, safe=True)
        app_id = self.db.applications.insert({
                'owner': owner_id,
                'client_id': '123456',
                'name': 'Example',
                'main_url': 'https://example.com',
                'callback_url': 'https://example.com/callback',
                'image_url': 'https://example.com/logo.png',
                'description': 'Example description',
                }, safe=True)

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/bad-callback',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Redirect URI does not match registered callback URL')

        # 2. Valid requests
        # simulate a cancel action
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '200 OK')

        res = self.testapp.post('/oauth2/endpoints/authorization', {
                'cancel': 'No thanks',
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'https://example.com')

        # authenticated user who hasn't authorized the app
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('is asking your permission for')
        res.mustcontain('Allow access')
        res.mustcontain('No, thanks')

        res = self.testapp.post('/oauth2/endpoints/authorization', {
                'submit': 'Authorize',
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(user['authorized_apps'], [app_id])
        grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        self.assertNotEqual(grant, None)
        code = grant['code']
        location = 'https://example.com/callback?code=%s' % code
        self.assertEqual(res.location, location)

        # authenticate user who has already authorize the app
        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '123456',
                'redirect_uri': 'https://example.com/callback',
                })
        self.assertEqual(res.status, '302 Found')
        new_grant = self.db.authorization_codes.find_one({
                'scope': DEFAULT_SCOPE,
                'client_id': '123456',
                'user': user_id,
                })
        self.assertNotEqual(new_grant, None)
        self.assertNotEqual(new_grant['_id'], grant['_id'])
        self.assertNotEqual(new_grant['code'], grant['code'])
        code = new_grant['code']
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
                'name': 'Example',
                'main_url': 'https://example.com',
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
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
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
                'name': 'Example',
                'main_url': 'https://example.com',
                }, safe=True)

        app_id2 = self.db.applications.insert({
                'client_id': '98765',
                'client_secret': 'secret2',
                'callback_url': 'https://example.com/callback2',
                'name': 'Example2',
                'main_url': 'https://example.com',
                }, safe=True)

        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
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

    def test_applications(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('John')
        res.mustcontain('Log out')
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
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('New Application')
        res.mustcontain('Name')
        res.mustcontain('Main URL')
        res.mustcontain('Callback URL')
        res.mustcontain('Production ready')
        res.mustcontain('Image URL')
        res.mustcontain('Description')

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
        self.assertEqual(app['production_ready'], False)
        self.assertEqual(app['image_url'], '')
        self.assertEqual(app['description'], '')

        # error if we don't fill all fields
        res = self.testapp.post('/oauth2/applications/new', {
                'name': 'Test Application',
                'callback_url': 'http://example.com/callback',
                'submit': 'submit',
                })
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('There was a problem with your submission')

        # The user hit the cancel button
        res = self.testapp.post('/oauth2/applications/new', {
                'cancel': 'Cancel',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/applications')

    def test_application_delete(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/new')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
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
                'production_ready': False,
                }, safe=True)

        res = self.testapp.get('/oauth2/applications/%s/delete' % str(app_id),
                               status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        self.db.applications.update({'_id': app_id}, {
                '$set': {'owner': user_id},
                }, safe=True)
        res = self.testapp.get('/oauth2/applications/%s/delete' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Delete Application <span>Test Application</span>')
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

    def test_application_edit(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/xxx/edit')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/xxx/edit',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        res = self.testapp.get(
            '/oauth2/applications/000000000000000000000000/edit',
            status=404)
        self.assertEqual(res.status, '404 Not Found')

        # create a valid app
        app_id = self.db.applications.insert({
                'owner': bson.ObjectId(),
                'name': 'Test Application',
                'main_url': 'http://example.com',
                'callback_url': 'http://example.com/callback',
                'production_ready': False,
                'image_url': 'http://example.com/image.png',
                'description': 'example description',
                'client_id': '123456',
                'client_secret': 'secret',
                }, safe=True)

        res = self.testapp.get('/oauth2/applications/%s/edit' % str(app_id),
                               status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        self.db.applications.update({'_id': app_id}, {
                '$set': {'owner': user_id},
                }, safe=True)
        res = self.testapp.get('/oauth2/applications/%s/edit' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Edit application <span>Test Application</span>')
        res.mustcontain('Name')
        res.mustcontain('Test Application')
        res.mustcontain('Main URL')
        res.mustcontain('http://example.com')
        res.mustcontain('Callback URL')
        res.mustcontain('http://example.com/callback')
        res.mustcontain('Production ready')
        res.mustcontain('Image URL')
        res.mustcontain('http://example.com/image.png')
        res.mustcontain('Description')
        res.mustcontain('example description')
        res.mustcontain('Client Id')
        res.mustcontain('123456')
        res.mustcontain('Client secret')
        res.mustcontain('secret')
        res.mustcontain('Save application')
        res.mustcontain('Delete application')
        res.mustcontain('Cancel')

        # Let's make some changes
        old_count = self.db.applications.count()
        res = self.testapp.post('/oauth2/applications/%s/edit' % str(app_id), {
                'name': 'Test Application 2',
                'main_url': 'http://example.com/new',
                'callback_url': 'http://example.com/new/callback',
                'production_ready': 'true',
                'image_url': 'http://example.com/image2.png',
                'description': 'example description 2',
                'client_id': '123456-2',
                'client_secret': 'secret2',
                'submit': 'Save changes',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/applications')
        new_app = self.db.applications.find_one(app_id)
        self.assertEqual(new_app['name'], 'Test Application 2')
        self.assertEqual(new_app['main_url'],
                         'http://example.com/new')
        self.assertEqual(new_app['callback_url'],
                         'http://example.com/new/callback')
        self.assertEqual(new_app['production_ready'], True)
        self.assertEqual(new_app['image_url'], 'http://example.com/image2.png')
        self.assertEqual(new_app['description'], 'example description 2')
        # the Id and Secret shouldn't change
        self.assertEqual(new_app['client_id'], '123456')
        self.assertEqual(new_app['client_secret'], 'secret')
        self.assertEqual(old_count, self.db.applications.count())

        # Try and invalid change
        res = self.testapp.post('/oauth2/applications/%s/edit' % str(app_id), {
                'submit': 'Save changes',
                })
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('There was a problem with your submission')
        res.mustcontain('Required')

        # The user hit the delete button
        res = self.testapp.post('/oauth2/applications/%s/edit' % str(app_id), {
                'delete': 'Delete',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location,
                         'http://localhost/oauth2/applications/%s/delete'
                         % str(app_id))

        # The user hit the cancel button
        res = self.testapp.post('/oauth2/applications/%s/edit' % str(app_id), {
                'cancel': 'Cancel',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/applications')

    def test_authorized_applications(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/authorized-applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/authorized-applications')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Authorized Applications')

    def test_revoke_application(self):
        # this view required authentication
        res = self.testapp.get('/oauth2/applications/xxx/revoke')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/oauth2/applications/xxx/revoke',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Invalid application id')

        res = self.testapp.get(
            '/oauth2/applications/000000000000000000000000/revoke',
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

        res = self.testapp.get('/oauth2/applications/%s/revoke' % str(app_id),
                               status=401)
        self.assertEqual(res.status, '401 Unauthorized')

        self.db.users.update({'_id': user_id}, {
                '$set': {'authorized_apps': [app_id]},
                }, safe=True)

        res = self.testapp.get('/oauth2/applications/%s/revoke' % str(app_id))
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Revoke authorization to application <span>Test Application</span>')

        res = self.testapp.post('/oauth2/applications/%s/revoke' % str(app_id), {
                'submit': 'Yes, I am sure',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/authorized-applications')
        user = self.db.users.find_one(user_id)
        self.assertEqual(user['authorized_apps'], [])

    def test_clients(self):
        res = self.testapp.get('/oauth2/clients')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Available Clients')

        # create a couple of apps
        self.db.applications.insert({
                'client_id': '123456',
                'name': 'Example app 1',
                'main_url': 'https://example.com',
                'callback_url': 'https://example.com/callback',
                'production_ready': True,
                'image_url': 'https://example.com/image.png',
                'description': 'example description',
                }, safe=True)
        self.db.applications.insert({
                'client_id': '654321',
                'name': 'Example app 2',
                'main_url': 'https://2.example.com',
                'callback_url': 'https://2.example.com/callback',
                'production_ready': False,
                }, safe=True)

        res = self.testapp.get('/oauth2/clients')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain(
            'Available Clients', 'Example app 1', 'https://example.com',
            'https://example.com/image.png', 'example description',
            no=('Example app 2', 'https://2.example.com'),
            )

