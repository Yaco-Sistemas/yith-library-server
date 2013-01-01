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

from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    clean_collections = ('passwords', 'access_codes', 'users')

    def setUp(self):
        super(ViewTests, self).setUp()

        self.access_code = '1234'
        self.auth_header = {'Authorization': 'Bearer %s' % self.access_code}
        self.user_id = self.db.users.insert({
                'provider_user_id': 'user1',
                'screen_name': 'User 1',
                'authorized_apps': [],
                }, safe=True)
        self.db.access_codes.insert({
                'code': self.access_code,
                'scope': None,
                'user': self.user_id,
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

        password_id = self.db.passwords.insert({
                'service': 'testing',
                'secret': 's3cr3t',
                'owner': self.user_id,
                }, safe=True)
        res = self.testapp.get('/passwords/%s' % str(password_id),
                               headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                'service': 'testing',
                'secret': 's3cr3t',
                'owner': str(self.user_id),
                '_id': str(password_id),
                })

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

        password_id = self.db.passwords.insert({
                'service': 'testing',
                'secret': 's3cr3t',
                'owner': self.user_id,
                }, safe=True)
        data = '{"service": "testing2", "secret": "sup3rs3cr3t", "_id": "%s"}' % str(password_id)
        res = self.testapp.put('/passwords/%s' % str(password_id),
                               data, headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.json, {
                'service': 'testing2',
                'secret': 'sup3rs3cr3t',
                'owner': str(self.user_id),
                'account': None,
                'creation': None,
                'expiration': None,
                'last_modification': None,
                'notes': None,
                'tags': None,
                '_id': str(password_id),
                })
        password = self.db.passwords.find_one(password_id)
        self.assertNotEqual(password, None)
        self.assertEqual(password['service'], 'testing2')
        self.assertEqual(password['secret'], 'sup3rs3cr3t')
        self.assertEqual(password['owner'], self.user_id)

        data = '{"service": "testing2", "secret": "sup3rs3cr3t", "_id": "000000000000000000000000"}'
        res = self.testapp.put('/passwords/000000000000000000000000',
                               data, headers=self.auth_header, status=404)
        self.assertEqual(res.status, '404 Not Found')
        self.assertEqual(res.body, b'{"message": "Password not found"}')

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
            'owner': self.user_id,
            }
        _id = self.db.passwords.insert(password, safe=True)
        count = self.db.passwords.count()

        res = self.testapp.delete('/passwords/' + str(_id),
                                  headers=self.auth_header)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, b'""')
        self.assertEqual(self.db.passwords.count(), count - 1)
