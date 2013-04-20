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

import datetime
import os
import unittest

from pyramid import testing

from yithlibraryserver.datetimeservice.testing import FakeDatetimeService
from yithlibraryserver.db import MongoDB
from yithlibraryserver.testing import MONGO_URI

from yithlibraryserver.contributions.models import include_sticker
from yithlibraryserver.contributions.models import create_donation


class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()
        os.environ['YITH_FAKE_DATETIME'] = '2013-1-2-10-11-02'

        self.request = testing.DummyRequest()
        self.request.datetime_service = FakeDatetimeService(self.request)
        self.request.db = self.db

    def tearDown(self):
        testing.tearDown()
        self.db.drop_collection('donations')
        del os.environ['YITH_FAKE_DATETIME']

    def test_include_sticker(self):
        self.assertFalse(include_sticker(1))
        self.assertTrue(include_sticker(5))
        self.assertTrue(include_sticker(10))

    def test_create_donation_no_sticker(self):
        self.request.user = None

        donation = create_donation(self.request, {
                'amount': 1,
                'firstname': 'John',
                'lastname': 'Doe',
                'city': 'Springfield',
                'country': 'Exampleland',
                'state': 'Example',
                'street': 'Main Street 10',
                'zip': '12345678',
                'email': 'john@example.com',
                })

        self.assertEqual(donation['firstname'], 'John')
        self.assertEqual(donation['lastname'], 'Doe')
        self.assertEqual(donation['city'], 'Springfield')
        self.assertEqual(donation['country'], 'Exampleland')
        self.assertEqual(donation['state'], 'Example')
        self.assertEqual(donation['street'], 'Main Street 10')
        self.assertEqual(donation['zip'], '12345678')
        self.assertEqual(donation['email'], 'john@example.com')
        self.assertEqual(donation['creation'],
                         datetime.datetime(2013, 1, 2, 10, 11, 2))
        self.assertEqual(donation['send_sticker'], False)
        self.assertEqual(donation['user'], None)

    def test_create_donation_with_sticker(self):
        self.request.user = None

        donation = create_donation(self.request, {
                'amount': 5,
                'firstname': 'John',
                'lastname': 'Doe',
                'city': 'Springfield',
                'country': 'Exampleland',
                'state': 'Example',
                'street': 'Main Street 10',
                'zip': '12345678',
                'email': 'john@example.com',
                })

        self.assertEqual(donation['firstname'], 'John')
        self.assertEqual(donation['lastname'], 'Doe')
        self.assertEqual(donation['city'], 'Springfield')
        self.assertEqual(donation['country'], 'Exampleland')
        self.assertEqual(donation['state'], 'Example')
        self.assertEqual(donation['street'], 'Main Street 10')
        self.assertEqual(donation['zip'], '12345678')
        self.assertEqual(donation['email'], 'john@example.com')
        self.assertEqual(donation['creation'],
                         datetime.datetime(2013, 1, 2, 10, 11, 2))
        self.assertEqual(donation['send_sticker'], True)
        self.assertEqual(donation['user'], None)

    def test_create_donation_with_user(self):
        self.request.user = {'_id': 'fake_user_id'}

        donation = create_donation(self.request, {
                'amount': 10,
                'firstname': 'John',
                'lastname': 'Doe',
                'city': 'Springfield',
                'country': 'Exampleland',
                'state': 'Example',
                'street': 'Main Street 10',
                'zip': '12345678',
                'email': 'john@example.com',
                })

        self.assertEqual(donation['firstname'], 'John')
        self.assertEqual(donation['lastname'], 'Doe')
        self.assertEqual(donation['city'], 'Springfield')
        self.assertEqual(donation['country'], 'Exampleland')
        self.assertEqual(donation['state'], 'Example')
        self.assertEqual(donation['street'], 'Main Street 10')
        self.assertEqual(donation['zip'], '12345678')
        self.assertEqual(donation['email'], 'john@example.com')
        self.assertEqual(donation['creation'],
                         datetime.datetime(2013, 1, 2, 10, 11, 2))
        self.assertEqual(donation['send_sticker'], True)
        self.assertEqual(donation['user'], 'fake_user_id')
