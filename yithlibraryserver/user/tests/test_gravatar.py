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

import unittest

from pyramid.testing import DummyRequest

from yithlibraryserver.compat import urlparse
from yithlibraryserver.user.gravatar import Gravatar


class GravatarTests(unittest.TestCase):

    def assertURLEqual(self, url1, url2):
        parts1 = urlparse.urlparse(url1)
        parts2 = urlparse.urlparse(url2)
        self.assertEqual(parts1.scheme, parts2.scheme)
        self.assertEqual(parts1.hostname, parts2.hostname)
        self.assertEqual(parts1.netloc, parts2.netloc)
        self.assertEqual(parts1.params, parts2.params)
        self.assertEqual(parts1.path, parts2.path)
        self.assertEqual(parts1.port, parts2.port)
        self.assertEqual(urlparse.parse_qs(parts1.query),
                         urlparse.parse_qs(parts2.query))

    def test_get_email(self):
        request = DummyRequest()
        request.user = None
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_email(), None)

        request = DummyRequest()
        request.user = {}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_email(), None)

        request = DummyRequest()
        request.user = {'email': ''}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_email(), None)

        request = DummyRequest()
        request.user = {'email': 'john@example.com'}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_email(), 'john@example.com')

    def test_has_avatar(self):
        request = DummyRequest()
        request.user = None
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertFalse(gravatar.has_avatar())

        request = DummyRequest()
        request.user = {'email': 'john@example.com'}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertTrue(gravatar.has_avatar())

    def test_email_hash(self):
        request = DummyRequest()
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_email_hash('john@example.com'),
                         'd4c74594d841139328695756648b6bd6')
        self.assertEqual(gravatar.get_email_hash('JOHN@EXAMPLE.COM'),
                         'd4c74594d841139328695756648b6bd6')

    def test_get_image_url(self):
        request = DummyRequest()
        request.user = None
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertEqual(gravatar.get_image_url(),
                         'http://localhost/default_gravatar.png')

        request = DummyRequest()
        request.user = {}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertURLEqual(gravatar.get_image_url(),
                            'http://localhost/default_gravatar.png')

        request = DummyRequest()
        request.user = {'email': ''}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertURLEqual(gravatar.get_image_url(),
                            'http://localhost/default_gravatar.png')

        request = DummyRequest()
        request.user = {'email': 'john@example.com'}
        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertURLEqual(
            gravatar.get_image_url(),
            'https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=32&d=http%3A%2F%2Flocalhost%2Fdefault_gravatar.png')

        gravatar = Gravatar(request, 'http://localhost/default_gravatar.png')
        self.assertURLEqual(
            gravatar.get_image_url(100),
            'https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=100&d=http%3A%2F%2Flocalhost%2Fdefault_gravatar.png')
