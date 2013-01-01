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
            self.assertEqual(exp.location, '/register')

        user_id = self.db.users.insert({'screen_name': 'John Doe'}, safe=True)

        self.config.testing_securitypolicy(userid=str(user_id))
        res = assert_authenticated_user_is_registered(request)
        self.assertEqual(res['_id'], user_id)
        self.assertEqual(res['screen_name'], 'John Doe')
