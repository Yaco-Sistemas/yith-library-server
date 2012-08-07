from deform import ValidationFailure

from mock import patch

from yithlibraryserver import testing


class DummyValidationFailure(ValidationFailure):

    def render(self):
        return 'dummy error'


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_login(self):
        res = self.testapp.get('/login')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in with Twitter')
        res.mustcontain('/twitter/login')

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
