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

from pyramid import testing

from yithlibraryserver.user.idp import add_identity_provider


class IdentityProviderTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_add_identity_provider(self):
        self.config.add_directive('add_identity_provider',
                                  add_identity_provider)

        self.config.add_identity_provider('provider1')

        request = testing.DummyRequest()

        self.assertTrue(hasattr(request.registry, 'identity_providers'))
        self.assertEqual(len(request.registry.identity_providers), 1)
        idp1 = request.registry.identity_providers[0]
        self.assertEqual(idp1.route_path, 'provider1_login')
        self.assertEqual(idp1.image_path, 'yithlibraryserver:static/img/provider1-logo.png')
        self.assertEqual(idp1.message, 'Log in with ${idp}')
