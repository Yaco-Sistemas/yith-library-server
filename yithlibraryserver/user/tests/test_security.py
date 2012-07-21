import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from yithlibraryserver.db import MongoDB
from yithlibraryserver.testing import MONGO_URI
from yithlibraryserver.user.security import get_authenticated_user


class SecurityTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('yithlibraryserver.user')
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('users')

    def test_get_authenticated_user(self):
        self.config.testing_securitypolicy(userid='john')

        request = testing.DummyRequest()
        request.db = self.db

        self.assertRaises(HTTPFound, get_authenticated_user, request)
        try:
            get_authenticated_user(request)
        except HTTPFound as exp:
            self.assertEqual(exp.location, 'http://example.com/register')

        user_id = self.db.users.insert({'screen_name': 'John Doe'}, safe=True)

        self.config.testing_securitypolicy(userid=str(user_id))
        res = get_authenticated_user(request)
        self.assertEqual(res['_id'], user_id)
        self.assertEqual(res['screen_name'], 'John Doe')
