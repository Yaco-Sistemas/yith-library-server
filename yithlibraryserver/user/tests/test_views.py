from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_login(self):
        res = self.testapp.get('/login')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in with Twitter')
        res.mustcontain('/twitter/login')

    def test_register_new_user(self):
        # this view required authentication
        res = self.testapp.get('/register')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Log in')

        # Log in
        self.set_user_cookie('twitter1')

        res = self.testapp.get('/register?screen_name=John')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain("Hi John! It looks like it's the first time you log into the Yith Library.")
        res.mustcontain("/register")
        res.mustcontain("Register into Yith Library")
        res.mustcontain("John")

        res = self.testapp.get('/register')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain("It looks like it's the first time you log into the Yith Library.")
        res.mustcontain("/register")
        res.mustcontain("Register into Yith Library")

        self.assertEqual(self.db.users.count(), 0)
        res = self.testapp.post('/register', {
                'screen_name': 'John',
                'next_url': 'http://localhost/foo/bar',
                'submit': 'Register into Yith Library',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/foo/bar')
        self.assertTrue('Set-Cookie' in res.headers)
        self.assertEqual(self.db.users.count(), 1)

    def test_logout(self):
        # Log in
        self.set_user_cookie('twitter1')

        res = self.testapp.get('/logout', status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')
        self.assertTrue('Set-Cookie' in res.headers)
        self.assertTrue('auth_tkt=""' in res.headers['Set-Cookie'])
