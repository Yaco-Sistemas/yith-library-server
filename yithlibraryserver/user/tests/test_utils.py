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
from yithlibraryserver.testing import MONGO_URI

from yithlibraryserver.user.analytics import GoogleAnalytics
from yithlibraryserver.user.analytics import USER_ATTR
from yithlibraryserver.user.utils import split_name, delete_user, update_user
from yithlibraryserver.user.utils import register_or_update


class UtilsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('yithlibraryserver.user')
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('users')

    def test_split_name(self):
        self.assertEqual(split_name('John Doe'),
                         ('John', 'Doe'))
        self.assertEqual(split_name('John'),
                         ('John', ''))
        self.assertEqual(split_name('John M Doe'),
                         ('John', 'M Doe'))
        self.assertEqual(split_name(''),
                         ('', ''))

    def test_delete_user(self):
        user_id = self.db.users.insert({
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': '',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id}, safe=True)
        n_users = self.db.users.count()
        self.assertTrue(delete_user(self.db, user))
        refreshed_user = self.db.users.find_one({'_id': user_id}, safe=True)
        self.assertEqual(None, refreshed_user)
        self.assertEqual(n_users - 1, self.db.users.count())

    def test_update_user(self):
        user_id = self.db.users.insert({
                'screen_name': 'John Doe',
                'first_name': 'John',
                'last_name': '',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id})
        update_user(self.db, user, {}, {})

        updated_user = self.db.users.find_one({'_id': user_id})
        # the user has not changed
        self.assertEqual(updated_user['screen_name'], user['screen_name'])
        self.assertEqual(updated_user['first_name'], user['first_name'])
        self.assertEqual(updated_user['last_name'], user['last_name'])

        # update the last_name
        update_user(self.db, user, {'last_name': 'Doe'}, {})
        updated_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(updated_user['last_name'], 'Doe')

        # add an email attribute
        update_user(self.db, user, {'email': 'john@example.com'}, {})
        updated_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(updated_user['email'], 'john@example.com')

        # if an attribute has no value, no update happens
        update_user(self.db, user, {'first_name': ''}, {})
        updated_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(updated_user['first_name'], 'John')

        # update a non existing attribute
        update_user(self.db, user, {'foo': 'bar'}, {})
        updated_user = self.db.users.find_one({'_id': user_id})
        self.assertFalse('foo' in updated_user)

        # update the same attribute within the last parameter
        update_user(self.db, user, {}, {'foo': 'bar'})
        updated_user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(updated_user['foo'], 'bar')

    def test_register_or_update(self):
        request = testing.DummyRequest()
        request.db = self.db
        request.session = {}
        request.google_analytics = GoogleAnalytics(request)
        response = register_or_update(request, 'skynet', 1, {
                'screen_name': 'JohnDoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'invented_attribute': 'foo',  # this will not be in the output
                }, '/next')
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/register')
        self.assertEqual(request.session['next_url'], '/next')
        self.assertEqual(request.session['user_info'], {
                'screen_name': 'JohnDoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'provider': 'skynet',
                'skynet_id': 1,
                })

        # try with an existing user
        user_id = self.db.users.insert({
                'skynet_id': 1,
                'screen_name': 'JohnDoe',
                'first_name': 'John',
                'last_name': '',
                }, safe=True)

        request = testing.DummyRequest()
        request.db = self.db
        request.session = {USER_ATTR: True}
        request.google_analytics = GoogleAnalytics(request)
        response = register_or_update(request, 'skynet', 1, {
                'screen_name': 'JohnDoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                }, '/next')
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/next')
        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(user['email'], 'john@example.com')
        self.assertEqual(user['last_name'], 'Doe')
        self.assertEqual(user[USER_ATTR], True)

        # maybe there is a next_url in the session
        request = testing.DummyRequest()
        request.db = self.db
        request.session = {'next_url': '/foo'}
        request.google_analytics = GoogleAnalytics(request)
        response = register_or_update(request, 'skynet', 1, {
                'screen_name': 'JohnDoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                }, '/next')
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/foo')
