import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from yithlibraryserver.db import MongoDB
from yithlibraryserver.testing import MONGO_URI
from yithlibraryserver.user.security import (
    get_user,
    assert_authenticated_user_is_registered,
    )


class SecurityTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('yithlibraryserver.user')
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('users')

    def test_get_user(self):
        request = testing.DummyRequest()
        request.db = self.db

        self.assertEqual(None, get_user(request))

        self.config.testing_securitypolicy(userid='john')
        self.assertEqual(None, get_user(request))

        user_id = self.db.users.insert({'screen_name': 'John Doe'}, safe=True)
        self.config.testing_securitypolicy(userid=str(user_id))
        self.assertEqual(get_user(request), {
                '_id': user_id,
                'screen_name': 'John Doe',
                })

    def test_assert_authenticated_user_is_registered(self):
        self.config.testing_securitypolicy(userid='john')

        request = testing.DummyRequest()
        request.db = self.db

        self.assertRaises(HTTPFound, assert_authenticated_user_is_registered, request)
        try:
            assert_authenticated_user_is_registered(request)
        except HTTPFound as exp:
            self.assertEqual(exp.location, 'http://example.com/register')

        user_id = self.db.users.insert({'screen_name': 'John Doe'}, safe=True)

        self.config.testing_securitypolicy(userid=str(user_id))
        res = assert_authenticated_user_is_registered(request)
        self.assertEqual(res['_id'], user_id)
        self.assertEqual(res['screen_name'], 'John Doe')
