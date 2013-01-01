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

import unittest

from pyramid import testing

from yithlibraryserver.db import MongoDB
from yithlibraryserver.password.models import PasswordsManager
from yithlibraryserver.testing import MONGO_URI


class PasswordsManagerTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()
        self.pm = PasswordsManager(self.db)
        self.user_id = self.db.users.insert({'name': 'John'}, safe=True)
        self.user = self.db.users.find_one({'_id': self.user_id}, safe=True)

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('users')
        self.db.drop_collection('passwords')

    def test_create(self):
        n_passwords = self.db.passwords.count()
        password = {'secret': 'secret1'}
        created_password = self.pm.create(self.user, password)
        self.assertEqual(created_password['owner'], self.user_id)
        self.assertTrue('_id' in created_password)
        self.assertEqual(n_passwords + 1, self.db.passwords.count())

    def test_retrieve(self):
        p1 = self.db.passwords.insert({
                'secret': 'secret1',
                'owner': self.user_id,
                }, safe=True)

        password = self.pm.retrieve(self.user, p1)
        self.assertEqual(password, {
                'secret': 'secret1',
                'owner': self.user_id,
                '_id': p1,
                })

        p2 = self.db.passwords.insert({
                'secret': 'secret2',
                'owner': self.user_id,
                }, safe=True)
        passwords = self.pm.retrieve(self.user)
        self.assertEqual(list(passwords), [{
                    'secret': 'secret1',
                    'owner': self.user_id,
                    '_id': p1,
                    }, {
                    'secret': 'secret2',
                    'owner': self.user_id,
                    '_id': p2,
                    }])

    def test_update(self):
        p1 = self.db.passwords.insert({
                'secret': 'secret1',
                'owner': self.user_id,
                }, safe=True)
        new_password = {'secret': 'new secret'}
        updated_password = self.pm.update(self.user, p1, new_password)
        self.assertEqual(updated_password, {
                '_id': p1,
                'owner': self.user_id,
                'secret': 'new secret',
                })

        fake_user = {'_id': '000000000000000000000000'}
        new_password['secret'] = 'another secret'
        updated_password = self.pm.update(fake_user, p1, new_password)
        self.assertEqual(None, updated_password)

    def test_delete(self):
        p1 = self.db.passwords.insert({
                'secret': 'secret1',
                'owner': self.user_id,
                }, safe=True)
        n_passwords = self.db.passwords.count()

        self.assertTrue(self.pm.delete(self.user, p1))
        self.assertEqual(n_passwords - 1, self.db.passwords.count())
        password = self.db.passwords.find_one({'_id': p1}, safe=True)
        self.assertEqual(None, password)

        p1 = self.db.passwords.insert({
                'secret': 'secret1',
                'owner': self.user_id,
                }, safe=True)
        p2 = self.db.passwords.insert({
                'secret': 'secret2',
                'owner': self.user_id,
                }, safe=True)
        n_passwords = self.db.passwords.count()
        self.assertTrue(self.pm.delete(self.user))
        self.assertEqual(n_passwords - 2, self.db.passwords.count())
        password1 = self.db.passwords.find_one({'_id': p1}, safe=True)
        self.assertEqual(None, password1)
        password2 = self.db.passwords.find_one({'_id': p2}, safe=True)
        self.assertEqual(None, password2)
