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


class FakeDatetimeService(object):

    def __init__(self, request):
        self.request = request
        self.mock = None

    def set_mock(self, mock):
        self.mock = mock

    def utcnow(self):
        if self.mock:
            return self.mock.utcnow()
        else:
            return datetime.datetime.utcnow()

    def date_today(self):
        if self.mock:
            return self.mock.today()
        else:
            return datetime.date.today()


def get_fake_datetime(request):
    return FakeDatetimeService(request)


def includeme(config):
    config.set_request_property(get_fake_datetime, 'datetime_service', reify=True)
