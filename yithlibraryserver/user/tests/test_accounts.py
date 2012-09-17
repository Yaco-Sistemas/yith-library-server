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
        self.assertEquals(('facebook', 'google', 'twitter'),
                          get_available_providers())

    def test_get_providers(self):
        self.assertEquals([], get_providers({}, ''))
        self.assertEquals([{'name': 'facebook', 'is_current': True}],
                          get_providers({'facebook_id': 1234}, 'facebook'))
        self.assertEquals([{
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
        self.assertEquals([], get_providers({'myspace_id': 1234}, ''))

    def test_n_passwords(self):
        self.assertEquals(0, get_n_passwords(self.db, {'_id': 1}))

        self.db.passwords.insert({'password': 'secret', 'owner': 1}, safe=True)
        self.assertEquals(1, get_n_passwords(self.db, {'_id': 1}))

        self.db.passwords.insert({'password2': 'secret2', 'owner': 1}, safe=True)
        self.assertEquals(2, get_n_passwords(self.db, {'_id': 1}))
        self.db.passwords.insert({'password2': 'secret2', 'owner': 2}, safe=True)
        self.assertEquals(2, get_n_passwords(self.db, {'_id': 1}))

    def test_get_accounts(self):
        self.assertEquals([], get_accounts(self.db, {}, ''))
        self.assertEquals([], get_accounts(self.db,
                                           {'email': 'john@example.com'}, ''))

        user_id = self.db.users.insert({'email': 'john@example.com'},
                                       safe=True)
        self.assertEquals([], get_accounts(self.db,
                                           {'email': 'john@example.com'}, ''))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'twitter_id': 1234},
                }, safe=True)
        self.assertEquals([], get_accounts(self.db,
                                           {'email': 'john@example.com'}, ''))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'email_verified': True},
                }, safe=True)
        self.assertEquals([{
                    'providers': [{
                            'name': 'twitter',
                            'is_current': True,
                            }],
                    'passwords': 0,
                    'id': str(user_id),
                    'is_current': True,
                    }],
                          get_accounts(self.db,
                                       {'email': 'john@example.com'},
                                       'twitter'))

        self.db.passwords.insert({'password': 'secret', 'owner': user_id},
                                 safe=True)
        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'twitter_id': 1234},
                }, safe=True)
        self.assertEquals([{
                    'providers': [{
                            'name': 'twitter',
                            'is_current': False,
                            }],
                    'passwords': 1,
                    'id': str(user_id),
                    'is_current': False,
                    }],
                          get_accounts(self.db,
                                       {'email': 'john@example.com'},
                                       'google'))

        self.db.users.update({'email': 'john@example.com'}, {
                '$set': {'google_id': 4321},
                }, safe=True)
        self.assertEquals([{
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
                    }],
                          get_accounts(self.db,
                                       {'email': 'john@example.com'},
                                       'google'))

    def test_merge_accounts(self):
        self.assertEquals(0, merge_accounts(self.db, {}, []))

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
        self.assertEquals(1, self.db.users.count())
        self.assertEquals(0, merge_accounts(self.db, master_user,
                                            [str(master_id)]))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEquals(master_user, master_user_reloaded)
        self.assertEquals(1, self.db.users.count())

        # merge with invented users does nothing neither
        self.assertEquals(0, merge_accounts(self.db, master_user,
                                            ['000000000000000000000000']))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEquals(master_user, master_user_reloaded)
        self.assertEquals(1, self.db.users.count())

        # let's create valid users
        other_id = self.db.users.insert({
                'email': 'john@example.com',
                'google_id': 4321,
                'authorized_apps': ['b', 'c'],
                }, safe=True)
        self.assertEquals(2, self.db.users.count())
        self.db.passwords.insert({
                'owner': other_id,
                'password2': 'secret2',
                }, safe=True)

        self.assertEquals(1, merge_accounts(self.db, master_user,
                                            [str(other_id)]))
        master_user_reloaded = self.db.users.find_one({'_id': master_id},
                                                      safe=True)
        self.assertEquals({
                '_id': master_id,
                'email': 'john@example.com',
                'twitter_id': 1234,
                'google_id': 4321,
                'authorized_apps': ['a', 'b', 'c'],
                }, master_user_reloaded)
        self.assertEquals(1, self.db.users.count())
        self.assertEquals(2,
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
        self.assertEquals(4, self.db.passwords.find(
                {'owner': user1_id}, safe=True).count())
        self.assertEquals(0, self.db.passwords.find(
                {'owner': user2_id}, safe=True).count())
        self.assertEquals(None, self.db.users.find_one({'_id': user2_id}))
        user1_refreshed = self.db.users.find_one({'_id': user1_id}, safe=True)
        self.assertEquals(user1_refreshed, {
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
