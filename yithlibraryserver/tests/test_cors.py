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

from yithlibraryserver.cors import CORSManager


class FakeRequest(object):

    def __init__(self, headers):
        self.headers = headers

FakeResponse = FakeRequest


class CORSManagerTests(unittest.TestCase):

    def test_cors_headers(self):
        cm = CORSManager('')

        request = FakeRequest({'Origin': 'foo'})
        response = FakeResponse({})

        cm.add_cors_header(request, response)

        self.assertEqual(response.headers, {})


        cm = CORSManager('http://localhost')

        request = FakeRequest({'Origin': 'http://localhost'})
        response = FakeResponse({})

        cm.add_cors_header(request, response)

        self.assertEqual(response.headers,
                         {'Access-Control-Allow-Origin': 'http://localhost'})
