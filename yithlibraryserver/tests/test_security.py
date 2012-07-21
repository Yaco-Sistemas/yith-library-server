from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized

from yithlibraryserver import testing
from yithlibraryserver.security import authorize_user


class AuthorizationTests(testing.TestCase):

    clean_collections = ('access_codes', 'users')

    def test_authorize_user(self):

        request = testing.FakeRequest(headers={})

        # The authorization header is required
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        request = testing.FakeRequest(
            headers={'Authorization': 'Basic foobar'})
        # Only the bearer method is allowed
        self.assertRaises(HTTPBadRequest, authorize_user, request)

        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid code
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        access_code_id = self.db.access_codes.insert({
                'code': '1234',
                'user': 'user1',
                }, safe=True)
        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid user
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        user_id = self.db.users.insert({
                'username': 'user1',
                }, safe=True)
        self.db.access_codes.update({'_id': access_code_id}, {
                '$set': {'user': user_id},
                }, safe=True)
        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid user
        authorized_user = authorize_user(request)
        self.assertEqual(authorized_user['username'], 'user1')
