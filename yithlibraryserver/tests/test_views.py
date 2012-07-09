import unittest

from webtest import TestApp

from yithlibraryserver import main


class ViewTests(unittest.TestCase):

    def setUp(self):
        app = main({}, mongo_uri='mongodb://localhost:27017/test-yith-library')
        self.testapp = TestApp(app)
        self.db = app.registry.settings['db_conn']['test-yith-library']

    def tearDown(self):
        self.db.drop_collection('passwords')

    def test_password_collection_options(self):
        res = self.testapp.options('/user')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET, POST')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Origin, Content-Type, Accept')

    def test_password_collection_get(self):
        res = self.testapp.get('/user1')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'[]')

    def test_password_collection_post(self):
        res = self.testapp.post('/user2', '', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "No JSON object could be decoded"}')

        res = self.testapp.post('/user2',
                                '{"secret": "s3cr3t", "service": "myservice"}')

        self.assertEqual(res.status, '200 OK')

    def test_password_options(self):
        res = self.testapp.options('/user3/123456')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET, PUT, DELETE')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Origin, Content-Type, Accept')

    def test_password_get(self):
        res = self.testapp.get('/user4/123456', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.get('/user4/000000000000000000000000',
                               status=404)
        self.assertEqual(res.status, '404 Not Found')
        self.assertEqual(res.body,
                         b'{"message": "Password not found"}')


    def test_password_put(self):
        res = self.testapp.put('/user5/123456', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.put('/user5/000000000000000000000000',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "No JSON object could be decoded"}')

    def test_password_delete(self):
        res = self.testapp.delete('/user6/123456', status=400)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertEqual(res.body,
                         b'{"message": "Invalid password id"}')

        res = self.testapp.delete('/user6/000000000000000000000000',
                               status=404)
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

        res = self.testapp.delete('/user6/' + str(_id))
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'""')
        self.assertEqual(self.db.passwords.count(), count - 1)
