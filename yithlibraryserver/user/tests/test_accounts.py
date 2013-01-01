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
from pyramid.testing import DummyRequest

from pyramid_mailer import get_mailer

from yithlibraryserver.db import MongoDB
from yithlibraryserver.user.accounts import get_available_providers
from yithlibraryserver.user.accounts import get_providers, get_n_passwords
from yithlibraryserver.user.accounts import get_accounts, merge_accounts
from yithlibraryserver.user.accounts import merge_users
from yithlibraryserver.user.accounts import notify_admins_of_account_removal
from yithlibraryserver.testing import MONGO_URI, TestCase


class AccountTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('users')
        self.db.drop_collection('passwords')

    def test_get_available_providers(self):
        self.assertEqual(('facebook', 'google', 'twitter', 'persona'),
                         get_available_providers())

    def test_get_providers(self):
        self.assertEqual([], get_providers({}, ''))
        self.assertEqual([{'name': 'facebook', 'is_current': True}],
                         get_providers({'facebook_id': 1234}, 'facebook'))
        self.assertEqual([{
                    'name': 'facebook',
                    'is_current': True,
                    }, {
                    'name': 'google',
                    'is_current': False,
                    }, {
                    'name': 'twitter',
                    'is_current': False,
                    }],
                          get_providers({'facebook_id': 1234,
                                         'google_id': 4321,
                                         'twitter_id': 6789}, 'facebook'))
        self.assertEqual([], get_providers({'myspace_id': 1234}, ''))

    def test_n_passwords(self):
        self.assertEqual(0, get_n_passwords(self.db, {'_id': 1}))

        self.db.passwords.insert({'password': 'secret', 'owner': 1}, safe=True)
        self.assertEqual(1, get_n_passwords(self.db, {'_id': 1}))

        self.db.passwords.insert({'password2': 'secret2', 'owner': 1}, safe=True)
        self.assertEqual(2, get_n_passwords(self.db, {'_id': 1}))
        self.db.passwords.insert({'password2': 'secret2', 'owner': 2}, safe=True)
        self.assertEqual(2, get_n_passwords(self.db, {'_id': 1}))

    def test_get_accounts(self):
        self.assertEqual([], get_accounts(self.db, {}, ''))
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, ''))

        user_id = self.db.users.insert({'email': 'john@example.com'},
                                       safe=True)
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }, {
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': str(user_id),
                    'is_verified': False,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, ''))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'twitter_id': 1234},
                }, safe=True)
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }, {
                    'providers': [{
                            'name': 'twitter',
                            'is_current': False,
                            }],
                    'is_current': False,
                    'passwords': 0,
                    'id': str(user_id),
                    'is_verified': False,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, ''))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'email_verified': True},
                }, safe=True)
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }, {
                    'providers': [{
                            'name': 'twitter',
                            'is_current': True,
                            }],
                    'passwords': 0,
                    'id': str(user_id),
                    'is_current': True,
                    'is_verified': True,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, 'twitter'))

        self.db.passwords.insert({'password': 'secret', 'owner': user_id},
                                 safe=True)
        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'twitter_id': 1234},
                }, safe=True)
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }, {
                    'providers': [{
                            'name': 'twitter',
                            'is_current': False,
                            }],
                    'passwords': 1,
                    'id': str(user_id),
                    'is_current': False,
                    'is_verified': True,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, 'google'))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'google_id': 4321},
                }, safe=True)
        self.assertEqual([{
                    'providers': [],
                    'is_current': False,
                    'passwords': 0,
                    'id': '',
                    'is_verified': False,
                    }, {
                    'providers': [{
                            'name': 'google',
                            'is_current': True,
                            }, {
                            'name': 'twitter',
                            'is_current': False,
                            }],
                    'passwords': 1,
                    'id': str(user_id),
                    'is_current': True,
                    'is_verified': True,
                    }], get_accounts(self.db, {
                    'email': 'john@example.com',
                    '_id': '',
                    }, 'google'))

    def test_merge_accounts(self):
        self.assertEqual(0, merge_accounts(self.db, {}, []))

        master_id = self.db.users.insert({
                'email': 'john@example.com',
                'twitter_id': 1234,
                'authorized_apps': ['a', 'b'],
                }, safe=True)
        master_user = self.db.users.find_one({'_id': master_id}, safe=True)

        self.db.passwords.insert({
                'owner': master_id,
                'password1': 'secret1',
                }, safe=True)

        # merging with itself does nothing
        self.assertEqual(1, self.db.users.count())
        self.assertEqual(0, merge_accounts(self.db, master_user,
                                            [str(master_id)]))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEqual(master_user, master_user_reloaded)
        self.assertEqual(1, self.db.users.count())

        # merge with invented users does nothing neither
        self.assertEqual(0, merge_accounts(self.db, master_user,
                                           ['000000000000000000000000']))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEqual(master_user, master_user_reloaded)
        self.assertEqual(1, self.db.users.count())

        # let's create valid users
        other_id = self.db.users.insert({
                'email': 'john@example.com',
                'google_id': 4321,
                'authorized_apps': ['b', 'c'],
                }, safe=True)
        self.assertEqual(2, self.db.users.count())
        self.db.passwords.insert({
                'owner': other_id,
                'password2': 'secret2',
                }, safe=True)

        self.assertEqual(1, merge_accounts(self.db, master_user,
                                           [str(other_id)]))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEqual({
                '_id': master_id,
                'email': 'john@example.com',
                'twitter_id': 1234,
                'google_id': 4321,
                'authorized_apps': ['a', 'b', 'c'],
                }, master_user_reloaded)
        self.assertEqual(1, self.db.users.count())
        self.assertEqual(2,
                         self.db.passwords.find({'owner': master_id}).count())

    def test_merge_users(self):
        user1_id = self.db.users.insert({
                'email': 'john@example.com',
                'twitter_id': 1234,
                'authorized_apps': ['a', 'b'],
                }, safe=True)
        self.db.passwords.insert({
                'owner': user1_id,
                'password': 'secret1',
                }, safe=True)
        self.db.passwords.insert({
                'owner': user1_id,
                'password': 'secret2',
                }, safe=True)
        user1 = self.db.users.find_one({'_id': user1_id}, safe=True)

        user2_id = self.db.users.insert({
                'email': 'john@example.com',
                'google_id': 4321,
                'authorized_apps': ['b', 'c'],
                }, safe=True)
        self.db.passwords.insert({
                'owner': user2_id,
                'password': 'secret3',
                }, safe=True)
        self.db.passwords.insert({
                'owner': user2_id,
                'password': 'secret4',
                }, safe=True)
        user2 = self.db.users.find_one({'_id': user2_id}, safe=True)

        merge_users(self.db, user1, user2)
        self.assertEqual(4, self.db.passwords.find(
                {'owner': user1_id}, safe=True).count())
        self.assertEqual(0, self.db.passwords.find(
                {'owner': user2_id}, safe=True).count())
        self.assertEqual(None, self.db.users.find_one({'_id': user2_id}))
        user1_refreshed = self.db.users.find_one({'_id': user1_id}, safe=True)
        self.assertEqual(user1_refreshed, {
                '_id': user1_id,
                'email': 'john@example.com',
                'twitter_id': 1234,
                'google_id': 4321,
                'authorized_apps': ['a', 'b', 'c'],
                })


class AccountRemovalNotificationTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.include('yithlibraryserver')
        super(AccountRemovalNotificationTests, self).setUp()

    def test_notify_admins_of_account_removal(self):
        request = DummyRequest()
        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 0)

        user = {'first_name': 'John', 'last_name': 'Doe',
                'email': 'john@example.com'}
        reason = 'I do not trust free services'
        admin_emails = ['admin1@example.com', 'admin2@example.com']
        notify_admins_of_account_removal(request, user, reason, admin_emails)

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                        'A user has destroyed his Yith Library account')
        self.assertEqual(mailer.outbox[0].recipients, admin_emails)
        self.assertTrue('John Doe <john@example.com' in mailer.outbox[0].body)
        self.assertTrue('I do not trust free services' in mailer.outbox[0].body)
