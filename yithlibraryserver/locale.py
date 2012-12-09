# Yith Library Server is a password storage server.
# Copyright (C) 2012 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

try:
    from babel.dates import format_date, format_datetime
except ImportError:
    # Babel does not work in Python 3

    def format_date(date_value, locale=None):
        return date_value.strftime('%c')

    def format_datetime(datetime_value, locale=None):
        return datetime_value.strftime('%c')


class DatesFormatter(object):

    def __init__(self, locale_name):
        self.locale_name = locale_name

    def date(self, date_value):
        return format_date(date_value, locale=self.locale_name)

    def datetime(self, datetime_value):
        return format_datetime(datetime_value, locale=self.locale_name)
