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
import unittest


from yithlibraryserver.datetimeservice import DateService, get_date
from yithlibraryserver.datetimeservice import DatetimeService, get_datetime


class DateServiceTests(unittest.TestCase):

    def assertDateEqual(self, date1, date2):
        delta = date2 - date1
        self.assertEqual(delta.days, 0)

    def test_dateservice(self):
        ds = DateService(None)
        self.assertTrue(isinstance(ds.today(), datetime.date))
        self.assertDateEqual(ds.today(), datetime.date.today())

    def test_get_date(self):
        request = object()
        date = get_date(request)
        self.assertTrue(isinstance(date, DateService))
        self.assertEqual(date.request, request)


class DatetimeServiceTests(unittest.TestCase):

    def assertDatetimeEqual(self, datetime1, datetime2):
        delta = datetime2 - datetime1
        self.assertEqual(delta.days, 0)
        self.assertTrue(delta.seconds < 2)

    def test_datetimeservice(self):
        ds = DatetimeService(None)
        self.assertTrue(isinstance(ds.utcnow(), datetime.datetime))
        self.assertDatetimeEqual(ds.utcnow(), datetime.datetime.utcnow())

    def test_get_datetime(self):
        request = object()
        datetime = get_datetime(request)
        self.assertTrue(isinstance(datetime, DatetimeService))
        self.assertEqual(datetime.request, request)
