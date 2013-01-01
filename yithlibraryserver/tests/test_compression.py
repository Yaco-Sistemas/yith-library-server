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

from yithlibraryserver import testing


class ContentEncodingTests(testing.TestCase):

    def test_identity_compression(self):
        res = self.testapp.get('/')  # Identity encoding is the default one
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_encoding, None)

        res = self.testapp.get('/', headers={'Accept-Encoding': 'identity'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_encoding, None)

    def test_gzip_compression(self):
        res = self.testapp.get('/', headers={'Accept-Encoding': 'gzip'})
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_encoding, 'gzip')
