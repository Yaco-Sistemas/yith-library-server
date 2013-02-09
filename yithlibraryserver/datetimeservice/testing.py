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


class FakeDateService(object):

    def __init__(self, request):
        self.request = request

    def today(self):
        fake = os.environ['YITH_FAKE_DATE']
        parts = [int(p) for p in fake.split('-')]
        return datetime.date(*parts)


class FakeDatetimeService(object):

    def __init__(self, request):
        self.request = request

    def utcnow(self):
        fake = os.environ['YITH_FAKE_DATETIME']
        parts = [int(p) for p in fake.split('-')]
        return datetime.datetime(*parts)


def get_fake_date(request):
    return FakeDateService(request)


def get_fake_datetime(request):
    return FakeDatetimeService(request)


def includeme(config):
    config.set_request_property(get_fake_date, 'date_service', reify=True)
    config.set_request_property(get_fake_datetime, 'datetime_service', reify=True)
