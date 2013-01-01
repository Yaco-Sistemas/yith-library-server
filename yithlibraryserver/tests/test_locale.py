# Yith Library Server is a password storage server.
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

import datetime
import unittest

from yithlibraryserver import locale


class DatesFormatterTests(unittest.TestCase):

    def test_date(self):
        df_en = locale.DatesFormatter('en')
        df_es = locale.DatesFormatter('es')

        date = datetime.date(2012, 12, 12)

        if locale.HAS_BABEL:
            self.assertEqual(df_en.date(date), 'Dec 12, 2012')
            self.assertEqual(df_es.date(date), '12/12/2012')

        locale_changed = False
        if locale.HAS_BABEL:
            locale.HAS_BABEL = False
            locale_changed = True

        self.assertEqual(df_en.date(date), 'Wed Dec 12 00:00:00 2012')
        self.assertEqual(df_es.date(date), 'Wed Dec 12 00:00:00 2012')

        if locale_changed:
            locale.HAS_BABEL = not locale.HAS_BABEL

    def test_datetime(self):
        df_en = locale.DatesFormatter('en')
        df_es = locale.DatesFormatter('es')

        date = datetime.datetime(2012, 12, 12, 12, 12, 12)

        if locale.HAS_BABEL:
            self.assertEqual(df_en.datetime(date), 'Dec 12, 2012 12:12:12 PM')
            self.assertEqual(df_es.datetime(date), '12/12/2012 12:12:12')

        locale_changed = False
        if locale.HAS_BABEL:
            locale.HAS_BABEL = False
            locale_changed = True

        self.assertEqual(df_en.datetime(date), 'Wed Dec 12 12:12:12 2012')
        self.assertEqual(df_es.datetime(date), 'Wed Dec 12 12:12:12 2012')

        if locale_changed:
            locale.HAS_BABEL = not locale.HAS_BABEL
