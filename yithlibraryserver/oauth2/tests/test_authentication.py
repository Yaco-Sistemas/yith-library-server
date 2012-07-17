from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver import testing
from yithlibraryserver.oauth2.authentication import authenticate_client
from yithlibraryserver.oauth2.authentication import auth_basic_encode


class AuthenticationTests(testing.TestCase):

    clean_collections = ('applications', )

    def test_authenticate_client(self):
        request = testing.FakeRequest({})
        # The authorization header is required
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        request = testing.FakeRequest({'Authorization': 'Advanced foobar'})
        # Only the basic method is allowed
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        request = testing.FakeRequest({
                'Authorization': 'Basic ' + auth_basic_encode('foo', 'bar'),
                }, self.db)
        # Invalid user:password
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        self.db.applications.insert({
                'client_id': '123456',
                'client_secret': 'secret',
                })
        request = testing.FakeRequest({
                'Authorization': 'Basic ' + auth_basic_encode('123456', 'secret'),
                }, self.db)
        res = authenticate_client(request)
        self.assertEqual(res['client_id'], '123456')
        self.assertEqual(res['client_secret'], 'secret')

    def test_auth_basic_encode(self):
        self.assertEqual(auth_basic_encode('foo', 'bar'),
                         'Zm9vOmJhcg==\n')
