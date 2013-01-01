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

import datetime

from deform import ValidationFailure

from mock import patch

from pyramid_mailer import get_mailer

from yithlibraryserver.compat import url_quote
from yithlibraryserver.testing import TestCase
from yithlibraryserver.user.analytics import USER_ATTR


class DummyValidationFailure(ValidationFailure):

    def render(self):
        return 'dummy error'


class BadCollection(object):

    def __init__(self, user=None):
        self.user = user

    def find_one(self, *args, **kwargs):
        return self.user

    def update(self, *args, **kwargs):
        return {'n': 0}


class BadDB(object):

    def __init__(self, user):
        self.users = BadCollection(user)
        self.passwords = BadCollection()


class ViewTests(TestCase):

    clean_collections = ('users', 'passwords', )

    def test_login(self):
        res = self.testapp.get('/login?param1=value1&param2=value2')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in with Twitter')
        res.mustcontain('/twitter/login')
        res.mustcontain(url_quote('param1=value1&param2=value2'))

        res = self.testapp.get('/login')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in with Twitter')
        res.mustcontain('/twitter/login')
        res.mustcontain('next_url=/')

    def test_register_new_user(self):
        res = self.testapp.get('/register', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing user info in the session')

        self.add_to_session({
                'next_url': 'http://localhost/foo/bar',
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    },
                })

        res = self.testapp.get('/register')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain("It looks like it's the first time you log into the Yith Library.")
        res.mustcontain("Register into Yith Library")
        res.mustcontain("John")
        res.mustcontain("Doe")
        res.mustcontain("john@example.com")

        self.assertEqual(self.db.users.count(), 0)
        res = self.testapp.post('/register', {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'submit': 'Register into Yith Library',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')
        self.assertEqual(self.db.users.count(), 1)
        user = self.db.users.find_one({'first_name': 'John'})
        self.assertFalse(user is None)
        self.assertEqual(user['first_name'], 'John')
        self.assertEqual(user['last_name'], 'Doe')
        self.assertEqual(user['email'], 'john@example.com')
        self.assertEqual(user['email_verified'], True)
        self.assertEqual(user['authorized_apps'], [])

        # the next_url and user_info keys are cleared at this point
        self.add_to_session({
                'next_url': 'http://localhost/foo/bar',
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    },
                })

        # if no email is provided at registration, the email is
        # not verified
        res = self.testapp.post('/register', {
                'first_name': 'John2',
                'last_name': 'Doe2',
                'email': '',
                'submit': 'Register into Yith Library',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')
        self.assertEqual(self.db.users.count(), 2)
        user = self.db.users.find_one({'first_name': 'John2'})
        self.assertFalse(user is None)
        self.assertEqual(user['first_name'], 'John2')
        self.assertEqual(user['last_name'], 'Doe2')
        self.assertEqual(user['email'], '')
        self.assertEqual(user['email_verified'], False)
        self.assertEqual(user['authorized_apps'], [])

        # the next_url and user_info keys are cleared at this point
        self.add_to_session({
                'next_url': 'http://localhost/foo/bar',
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': '',
                    },
                })

        # if an email is provided at registration, but
        # there is no email in the session (the provider
        # did not gave it to us) the email is not verified
        # and a verification email is sent
        res = self.testapp.post('/register', {
                'first_name': 'John2',
                'last_name': 'Doe2',
                'email': 'john@example.com',
                'submit': 'Register into Yith Library',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')
        self.assertEqual(self.db.users.count(), 3)
        user = self.db.users.find_one({'first_name': 'John2'})
        self.assertFalse(user is None)
        self.assertEqual(user['first_name'], 'John2')
        self.assertEqual(user['last_name'], 'Doe2')
        self.assertEqual(user['email'], '')
        self.assertEqual(user['email_verified'], False)
        self.assertEqual(user['authorized_apps'], [])

        # check that the email was sent
        res.request.registry = self.testapp.app.registry
        mailer = get_mailer(res.request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         'Please verify your email address')
        self.assertEqual(mailer.outbox[0].recipients,
                         ['john@example.com'])


        # the next_url and user_info keys are cleared at this point
        self.add_to_session({
                'next_url': 'http://localhost/foo/bar',
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': '',
                    },
                USER_ATTR: True,
                })

        # The user want the Google Analytics cookie
        res = self.testapp.post('/register', {
                'first_name': 'John3',
                'last_name': 'Doe3',
                'email': 'john3@example.com',
                'submit': 'Register into Yith Library',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')
        self.assertEqual(self.db.users.count(), 4)
        user = self.db.users.find_one({'first_name': 'John3'})
        self.assertFalse(user is None)
        self.assertEqual(user['first_name'], 'John3')
        self.assertEqual(user['last_name'], 'Doe3')
        self.assertEqual(user['email'], 'john3@example.com')
        self.assertEqual(user['email_verified'], False)
        self.assertEqual(user['authorized_apps'], [])
        self.assertEqual(user[USER_ATTR], True)

        # the next_url and user_info keys are cleared at this point
        self.add_to_session({
                'next_url': 'http://localhost/foo/bar',
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    },
                })

        # simulate a cancel
        res = self.testapp.post('/register', {
                'cancel': 'Cancel',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')

        # same thing but no next_url in the session
        self.add_to_session({
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    },
                })
        res = self.testapp.post('/register', {
                'cancel': 'Cancel',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/oauth2/clients')

        # make the form fail
        self.add_to_session({
                'user_info': {
                    'provider': 'myprovider',
                    'myprovider_id': '1234',
                    'screen_name': 'John Doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    },
                })

        with patch('deform.Form.validate') as fake:
            fake.side_effect = DummyValidationFailure('f', 'c', 'e')
            res = self.testapp.post('/register', {
                    'submit': 'Register into Yith Library',
                    })
            self.assertEqual(res.status, '200 OK')

    def test_logout(self):
        # Log in
        self.set_user_cookie('twitter1')
        self.add_to_session({
                'current_provider': 'twitter',
                })

        res = self.testapp.get('/logout', status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')
        self.assertTrue('Set-Cookie' in res.headers)
        self.assertTrue('auth_tkt=""' in res.headers['Set-Cookie'])
        self.assertFalse('current_provider' in self.get_session(res))

    def test_user_information(self):
        # this view required authentication
        res = self.testapp.get('/profile')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        date = datetime.datetime(2012, 12, 12, 12, 12)
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'email_verified': False,
                'authorized_apps': [],
                'date_joined': date,
                'last_login': date,
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/profile')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Profile')
        res.mustcontain('John')
        res.mustcontain('Doe')
        res.mustcontain('Save changes')

        res = self.testapp.post('/profile', {
                'submit': 'Save changes',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/profile')
        # check that the user has changed
        new_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(new_user['first_name'], 'John')
        self.assertEqual(new_user['last_name'], 'Doe')
        self.assertEqual(new_user['email'], 'john@example.com')

        # make the form fail
        with patch('deform.Form.validate') as fake:
            fake.side_effect = DummyValidationFailure('f', 'c', 'e')
            res = self.testapp.post('/profile', {
                    'submit': 'Save Changes',
                    })
            self.assertEqual(res.status, '200 OK')

        # make the db fail
        with patch('yithlibraryserver.db.MongoDB.get_database') as fake:
            fake.return_value = BadDB(new_user)
            res = self.testapp.post('/profile', {
                    'submit': 'Save changes',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    })
            self.assertEqual(res.status, '200 OK')
            res.mustcontain('There were an error while saving your changes')

    def test_user_preferences(self):
        # this view required authentication
        res = self.testapp.get('/preferences')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        date = datetime.datetime(2012, 12, 12, 12, 12)
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'email_verified': False,
                'authorized_apps': [],
                'date_joined': date,
                'last_login': date,
                'allow_google_analytics': False,
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/preferences')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Preferences', 'Allow statistics cookie',
                        'Save changes')

        res = self.testapp.post('/preferences', {
                'submit': 'Save changes',
                'allow_google_analytics': 'true',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/preferences')
        # check that the user has changed
        new_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(new_user['allow_google_analytics'], True)

        # make the form fail
        with patch('deform.Form.validate') as fake:
            fake.side_effect = DummyValidationFailure('f', 'c', 'e')
            res = self.testapp.post('/preferences', {
                    'submit': 'Save Changes',
                    })
            self.assertEqual(res.status, '200 OK')

        # make the db fail
        with patch('yithlibraryserver.db.MongoDB.get_database') as fake:
            fake.return_value = BadDB(new_user)
            res = self.testapp.post('/preferences', {
                    'submit': 'Save changes',
                    'allow_google_analytics': 'true',
                    })
            self.assertEqual(res.status, '200 OK')
            res.mustcontain('There were an error while saving your changes')

    def test_destroy(self):
        # this view required authentication
        res = self.testapp.get('/destroy')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/destroy')
        res.mustcontain('Destroy account')
        res.mustcontain('Do you really really really want to destroy your account?')
        res.mustcontain('You will not be able to undo this operation')

        # simulate a cancel
        res = self.testapp.post('/destroy', {
                'cancel': 'Cancel',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/profile')

        # make the form fail
        with patch('deform.Form.validate') as fake:
            fake.side_effect = DummyValidationFailure('f', 'c', 'e')
            res = self.testapp.post('/destroy', {
                    'reason': '',
                    'submit': 'Yes, I am sure. Destroy my account',
                    })
            self.assertEqual(res.status, '200 OK')

        # now the real one
        res = self.testapp.post('/destroy', {
                'reason': 'I do not need a password manager',
                'submit': 'Yes, I am sure. Destroy my account',
                }, status=302)
        self.assertEqual(res.location, 'http://localhost/')
        self.assertTrue('Set-Cookie' in res.headers)
        self.assertTrue('auth_tkt=""' in res.headers['Set-Cookie'])

        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(None, user)

        res.request.registry = self.testapp.app.registry
        mailer = get_mailer(res.request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         'A user has destroyed his Yith Library account')
        self.assertEqual(mailer.outbox[0].recipients,
                         ['admin1@example.com', 'admin2@example.com'])
        self.assertTrue('I do not need a password manager' in mailer.outbox[0].body)


    def test_send_email_verification_code(self):
        # this view required authentication
        res = self.testapp.get('/send-email-verification-code')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'authorized_apps': [],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        # the user has no email so an error is expected
        res = self.testapp.get('/send-email-verification-code')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                'status': 'bad',
                'error': 'You have not an email in your profile',
                })

        # let's give the user an email
        self.db.users.update({'_id': user_id},
                             {'$set': {'email': 'john@example.com'}},
                             safe=True)

        # the request must be a post
        res = self.testapp.get('/send-email-verification-code')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                'status': 'bad',
                'error': 'Not a post',
                })


        # now a good request
        res = self.testapp.post('/send-email-verification-code', {
                'submit': 'Send verification code'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                'status': 'ok',
                'error': None,
                })
        res.request.registry = self.testapp.app.registry
        mailer = get_mailer(res.request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         'Please verify your email address')
        self.assertEqual(mailer.outbox[0].recipients,
                         ['john@example.com'])

        # simulate a db failure
        with patch('yithlibraryserver.user.email_verification.EmailVerificationCode.store') as fake:
            fake.return_value = False
            res = self.testapp.post('/send-email-verification-code', {
                    'submit': 'Send verification code'})
            self.assertEqual(res.status, '200 OK')
            self.assertEqual(res.json, {
                    'status': 'bad',
                    'error': 'There were problems storing the verification code',
                    })

    def test_verify_email(self):
        res = self.testapp.get('/verify-email', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing code parameter')

        res = self.testapp.get('/verify-email?code=1234', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing email parameter')

        res = self.testapp.get('/verify-email?code=1234&email=john@example.com')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Sorry, your verification code is not correct or has expired')

        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verification_code': '1234',
                'authorized_apps': [],
                }, safe=True)

        res = self.testapp.get('/verify-email?code=1234&email=john@example.com')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Congratulations, your email has been successfully verified')

        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(user['email_verified'], True)
        self.assertFalse('email_verification_code' in user)

    def test_identity_providers(self):
        # this view required authentication
        res = self.testapp.get('/identity-providers')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        user1_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                'authorized_apps': ['app1', 'app2'],
                }, safe=True)
        self.set_user_cookie(str(user1_id))
        self.db.passwords.insert({
                'owner': user1_id,
                'password': 'secret1',
                })

        # one account is not enough for merging
        res = self.testapp.post('/identity-providers', {
                'submit': 'Merge my accounts',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('You do not have enough accounts to merge')

        # so let's create another account with the same email
        user2_id = self.db.users.insert({
                'google_id': 'google1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                'authorized_apps': ['app2', 'app3'],
                }, safe=True)
        self.db.passwords.insert({
                'owner': user2_id,
                'password': 'secret2',
                })

        # now the profile view should say I can merge my accounts
        res = self.testapp.get('/identity-providers')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('You are registered with the following accounts',
                        'Merge my accounts',
                        'If you merge your accounts')

        # if only one account is selected or fake accounts
        # are selected nothing is merged
        res = self.testapp.post('/identity-providers', {
                'account-%s' % str(user1_id): 'on',
                'account-000000000000000000000000': 'on',
                'submit': 'Merge my accounts',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/identity-providers')
        self.assertEqual(2, self.db.users.count())
        self.assertEqual(1, self.db.passwords.find(
                {'owner': user1_id}, safe=True).count())
        self.assertEqual(1, self.db.passwords.find(
                {'owner': user2_id}, safe=True).count())

        # let's merge them
        res = self.testapp.post('/identity-providers', {
                'account-%s' % str(user1_id): 'on',
                'account-%s' % str(user2_id): 'on',
                'submit': 'Merge my accounts',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/identity-providers')

        # the accounts have been merged
        self.assertEqual(1, self.db.users.count())
        user1_refreshed = self.db.users.find_one({'_id': user1_id}, safe=True)
        self.assertEqual(user1_refreshed['google_id'], 'google1')
        self.assertEqual(user1_refreshed['authorized_apps'],
                         ['app1', 'app2', 'app3'])

        user2_refreshed = self.db.users.find_one({'_id': user2_id}, safe=True)
        self.assertEqual(user2_refreshed, None)

        self.assertEqual(2, self.db.passwords.find(
                {'owner': user1_id}, safe=True).count())

    def test_google_analytics_preference(self):
        res = self.testapp.post('/google-analytics-preference', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing preference parameter')

        # Anonymous users save the preference in the session
        res = self.testapp.post('/google-analytics-preference', {'yes': 'Yes'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {'allow': True})
        self.assertEqual(self.get_session(res)[USER_ATTR], True)

        res = self.testapp.post('/google-analytics-preference', {'no': 'No'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {'allow': False})
        self.assertEqual(self.get_session(res)[USER_ATTR], False)

        # Authenticated users save the preference in the database
        # Log in
        user_id = self.db.users.insert({
                'twitter_id': 'twitter1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                'authorized_apps': ['app1', 'app2'],
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.post('/google-analytics-preference', {'yes': 'Yes'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {'allow': True})
        user_refreshed = self.db.users.find_one({'_id': user_id}, safe=True)
        self.assertEqual(user_refreshed[USER_ATTR], True)

        res = self.testapp.post('/google-analytics-preference', {'no': 'No'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {'allow': False})
        user_refreshed = self.db.users.find_one({'_id': user_id}, safe=True)
        self.assertEqual(user_refreshed[USER_ATTR], False)


class RESTViewTests(TestCase):

    clean_collections = ('users', 'access_codes')

    def setUp(self):
        super(RESTViewTests, self).setUp()

        self.access_code = '1234'
        self.auth_header = {'Authorization': 'Bearer %s' % self.access_code}
        date = datetime.datetime(2012, 12, 12, 12, 12)
        self.user_id = self.db.users.insert({
                'provider_user_id': 'user1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                'allow_google_analytics': True,
                'authorized_apps': [],
                'date_joined': date,
                'last_login': date,
                }, safe=True)
        self.db.access_codes.insert({
                'code': self.access_code,
                'scope': None,
                'user': self.user_id,
                'client_id': None,
                }, safe=True)

    def test_user_options(self):
        res = self.testapp.options('/user')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Origin, Content-Type, Accept, Authorization')

    def test_user_get(self):
        res = self.testapp.get('/user', headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                '_id': str(self.user_id),
                'provider_user_id': 'user1',
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                'allow_google_analytics': True,
                'authorized_apps': [],
                'date_joined': '2012-12-12T12:12:00+00:00',
                'last_login': '2012-12-12T12:12:00+00:00',
                })
