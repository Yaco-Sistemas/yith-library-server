# Yith Library Server is a password storage server.
# Copyright (C) 2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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
from yithlibraryserver.sna_callbacks import facebook_callback, google_callback
from yithlibraryserver.testing import MONGO_URI


class SNACallbackTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('yithlibraryserver')
        self.config.include('yithlibraryserver.user')
        self.request = testing.DummyRequest()
        self.request.session = {}
        mdb = MongoDB(MONGO_URI)
        self.request.db = mdb.get_database()

    def tearDown(self):
        testing.tearDown()

    def test_facebook_callback(self):
        result = facebook_callback(self.request, '123', {
            'screen_name': 'John Doe',
            'name': 'John Doe',
            'email': 'john@example.com',
            'username': 'john.doe',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertEqual(result.status, '302 Found')
        self.assertEqual(result.location, '/register')

    def test_google_callback(self):
        result = google_callback(self.request, '123', {
            'screen_name': 'John Doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertEqual(result.status, '302 Found')
        self.assertEqual(result.location, '/register')

