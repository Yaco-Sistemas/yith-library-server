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

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver import testing
from yithlibraryserver.oauth2.authentication import authenticate_client
from yithlibraryserver.oauth2.authentication import auth_basic_encode


class AuthenticationTests(testing.TestCase):

    clean_collections = ('applications', )

    def test_authenticate_client(self):
        request = testing.FakeRequest(headers={})
        # The authorization header is required
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        request = testing.FakeRequest(
            headers={'Authorization': 'Advanced foobar'})
        # Only the basic method is allowed
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        request = testing.FakeRequest(headers={
                'Authorization': auth_basic_encode('foo', 'bar'),
                }, db=self.db)
        # Invalid user:password
        self.assertRaises(HTTPUnauthorized, authenticate_client, request)

        self.db.applications.insert({
                'client_id': '123456',
                'client_secret': 'secret',
                })
        request = testing.FakeRequest(headers={
                'Authorization': auth_basic_encode('123456', 'secret'),
                }, db=self.db)
        res = authenticate_client(request)
        self.assertEqual(res['client_id'], '123456')
        self.assertEqual(res['client_secret'], 'secret')

    def test_auth_basic_encode(self):
        self.assertEqual(auth_basic_encode('foo', 'bar'),
                         'Basic Zm9vOmJhcg==\n')
