from yithlibraryserver import testing
from yithlibraryserver.oauth2.authorization import AuthorizationCodes
from yithlibraryserver.oauth2.authorization import AccessCodes
from yithlibraryserver.oauth2.authorization import Authorizator


class AuthorizationTests(testing.TestCase):

    clean_collections = ('authorization_codes', 'access_codes', 'user')

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
