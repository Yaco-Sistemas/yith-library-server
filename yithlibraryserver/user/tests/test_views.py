from deform import ValidationFailure

from mock import patch

from yithlibraryserver import testing
from yithlibraryserver.compat import url_quote


class DummyValidationFailure(ValidationFailure):

    def render(self):
        return 'dummy error'


class BadCollection(object):

    def __init__(self, user):
        self.user = user

    def find_one(self, *args, **kwargs):
        return self.user

    def update(self, *args, **kwargs):
        return {'n': 0}


class BadDB(object):

    def __init__(self, user):
        self.users = BadCollection(user)


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

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
        self.assertEqual(res.location, 'http://localhost/')

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

        res = self.testapp.get('/logout', status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')
        self.assertTrue('Set-Cookie' in res.headers)
        self.assertTrue('auth_tkt=""' in res.headers['Set-Cookie'])

    def test_user_profile(self):
        # this view required authentication
        res = self.testapp.get('/profile')
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

        res = self.testapp.get('/profile')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Profile')
        res.mustcontain('John')
        res.mustcontain('Doe')
        res.mustcontain('Save changes')
        res.mustcontain('Cancel')

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

        # click on the cancel button
        res = self.testapp.post('/profile', {
                'cancel': 'Cancel',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/profile')

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
