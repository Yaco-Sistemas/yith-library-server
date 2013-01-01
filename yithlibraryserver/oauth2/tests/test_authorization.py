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
from yithlibraryserver.oauth2.authorization import AuthorizationCodes
from yithlibraryserver.oauth2.authorization import AccessCodes
from yithlibraryserver.oauth2.authorization import Authorizator


class AuthorizationTests(testing.TestCase):

    clean_collections = ('authorization_codes', 'access_codes', 'users')

    def test_authorization_codes(self):
        codes = AuthorizationCodes(self.db)
        url = codes.get_redirect_url('1234', 'http://example.com', 'test')
        self.assertEqual(url, 'http://example.com?code=1234&state=test')
        url = codes.get_redirect_url('1234', 'http://example.com')
        self.assertEqual(url, 'http://example.com?code=1234')

        self.assertEqual(self.db.authorization_codes.count(), 0)
        code1 = codes.create('user1', 'client1', 'passwords')
        self.assertEqual(self.db.authorization_codes.count(), 1)

        # creating a code with same arguments replace the old one
        code2 = codes.create('user1', 'client1', 'passwords')
        self.assertEqual(self.db.authorization_codes.count(), 1)

        self.assertNotEqual(code1, code2)

        self.assertNotEqual(None, codes.find(code2))
        self.assertEqual(None, codes.find(code1))

        codes.remove(codes.find(code1))
        self.assertEqual(self.db.authorization_codes.count(), 0)

    def test_access_codes(self):
        codes = AccessCodes(self.db)
        self.assertEqual(self.db.access_codes.count(), 0)
        grant = {'scope': 'passwords', 'client_id': 'client1'}
        code1 = codes.create('user1', grant)
        self.assertEqual(self.db.access_codes.count(), 1)

        # creating a code with same arguments replace the old one
        code2 = codes.create('user1', grant)
        self.assertEqual(self.db.access_codes.count(), 1)

        self.assertNotEqual(code1, code2)

        self.assertNotEqual(None, codes.find(code2))
        self.assertEqual(None, codes.find(code1))

        codes.remove(codes.find(code1))
        self.assertEqual(self.db.access_codes.count(), 0)

    def test_authorizator(self):
        app = {'_id': 'app1'}
        authorizator = Authorizator(self.db, app)
        self.assertTrue(isinstance(authorizator.auth_codes,
                                   AuthorizationCodes))
        self.assertTrue(isinstance(authorizator.access_codes,
                                   AccessCodes))
        user = {'name': 'John Doe', 'authorized_apps': []}
        self.db.users.insert(user, safe=True)

        self.assertFalse(authorizator.is_app_authorized(user))

        authorizator.store_user_authorization(user)
        user = self.db.users.find_one({'name': 'John Doe'})

        self.assertTrue(authorizator.is_app_authorized(user))
        self.assertEqual(user['authorized_apps'], ['app1'])

        authorizator.remove_user_authorization(user)
        user = self.db.users.find_one({'name': 'John Doe'})

        self.assertFalse(authorizator.is_app_authorized(user))
        self.assertFalse('app1' in user['authorized_apps'])
