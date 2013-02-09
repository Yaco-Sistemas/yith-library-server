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

import os
import datetime
import unittest


from yithlibraryserver.datetimeservice.testing import FakeDateService, get_fake_date
from yithlibraryserver.datetimeservice.testing import FakeDatetimeService, get_fake_datetime


class FakeDateServiceTests(unittest.TestCase):

    def assertDateEqual(self, date1, date2):
        delta = date2 - date1
        self.assertEqual(delta.days, 0)

    def test_dateservice(self):
        ds = FakeDateService(None)
        fake_today = datetime.date(2012, 1, 10)
        os.environ['YITH_FAKE_DATE'] = '2012-1-10'
        self.assertTrue(isinstance(ds.today(), datetime.date))
        self.assertDateEqual(ds.today(), fake_today)
        del os.environ['YITH_FAKE_DATE']

    def test_get_fake_date(self):
        request = object()
        date = get_fake_date(request)
        self.assertTrue(isinstance(date, FakeDateService))
        self.assertEqual(date.request, request)


class FakeDatetimeServiceTests(unittest.TestCase):

    def assertDatetimeEqual(self, datetime1, datetime2):
        delta = datetime2 - datetime1
        self.assertEqual(delta.days, 0)
        self.assertTrue(delta.seconds < 2)

    def test_fakedatetimeservice(self):
        ds = FakeDatetimeService(None)
        os.environ['YITH_FAKE_DATETIME'] = '2012-1-10-14-23-01'
        fake_utcnow = datetime.datetime(2012, 1, 10, 14, 23, 01, 0)
        self.assertTrue(isinstance(ds.utcnow(), datetime.datetime))
        self.assertDatetimeEqual(ds.utcnow(), fake_utcnow)
        del os.environ['YITH_FAKE_DATETIME']

    def test_get_fakedatetime(self):
        request = object()
        datetime = get_fake_datetime(request)
        self.assertTrue(isinstance(datetime, FakeDatetimeService))
        self.assertEqual(datetime.request, request)
