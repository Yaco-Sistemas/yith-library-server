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
