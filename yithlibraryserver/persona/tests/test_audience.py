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

from yithlibraryserver.persona.audience import get_audience


class AudienceTests(unittest.TestCase):

    def test_get_audience(self):
        self.assertEqual(get_audience('http://localhost/'),
                         'http://localhost:80')

        self.assertEqual(get_audience('https://localhost:443/'),
                         'https://localhost:443')

        self.assertEqual(get_audience('https://localhost/foo'),
                         'https://localhost:443')

        self.assertRaises(ValueError, get_audience, 'foo://localhost')
