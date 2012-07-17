from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    clean_collections = ('passwords', 'access_codes', 'users')

    def setUp(self):
        super(ViewTests, self).setUp()

        self.access_code = '1234'
        self.auth_header = {'Authorization': 'Bearer %s' % self.access_code}
        user_id = self.db.users.insert({
                'provider_user_id': 'user1',
                'screen_name': 'User 1',
                'authorized_apps': [],
                }, safe=True)
        self.db.access_codes.insert({
                'code': self.access_code,
                'scope': None,
                'user': user_id,
                'client_id': None,
                }, safe=True)

    def test_password_collection_options(self):
        res = self.testapp.options('/passwords')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET, POST')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Origin, Content-Type, Accept, Authorization')

    def test_password_collection_get(self):
        res = self.testapp.get('/passwords', headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'[]')

    def test_password_collection_post(self):
        res = self.testapp.post('/passwords', '', headers=self.auth_header,
                                status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "No JSON object could be decoded"}')

        res = self.testapp.post('/passwords',
                                '{"secret": "s3cr3t", "service": "myservice"}',
                                headers=self.auth_header)

        self.assertEqual(res.status, '200 OK')

    def test_password_options(self):
        res = self.testapp.options('/passwords/123456')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET, PUT, DELETE')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Origin, Content-Type, Accept, Authorization')

    def test_password_get(self):
        res = self.testapp.get('/passwords/123456', headers=self.auth_header,
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.get('/passwords/000000000000000000000000',
                               headers=self.auth_header,
                               status=404)
        self.assertEqual(res.status, '404 Not Found')
        self.assertEqual(res.body,
                         b'{"message": "Password not found"}')


    def test_password_put(self):
        res = self.testapp.put('/passwords/123456', headers=self.auth_header,
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.put('/passwords/000000000000000000000000',
                               headers=self.auth_header, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "No JSON object could be decoded"}')

    def test_password_delete(self):
        res = self.testapp.delete('/passwords/123456',
                                  headers=self.auth_header, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.delete('/passwords/000000000000000000000000',
                                  headers=self.auth_header, status=404)
        self.assertEqual(res.status, '404 Not Found')
        self.assertEqual(res.body,
                         b'{"message": "Password not found"}')

        password = {
            'secret': 's3cr3t',
            'service': 'myservice',
            'owner': 'user6',
            }
        _id = self.db.passwords.insert(password, safe=True)
        count = self.db.passwords.count()

        res = self.testapp.delete('/passwords/' + str(_id),
                                  headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'""')
        self.assertEqual(self.db.passwords.count(), count - 1)
