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

from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized

from yithlibraryserver import testing
from yithlibraryserver.security import authorize_user


class AuthorizationTests(testing.TestCase):

    clean_collections = ('access_codes', 'users')

    def test_authorize_user(self):

        request = testing.FakeRequest(headers={})

        # The authorization header is required
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        request = testing.FakeRequest(
            headers={'Authorization': 'Basic foobar'})
        # Only the bearer method is allowed
        self.assertRaises(HTTPBadRequest, authorize_user, request)

        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid code
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        access_code_id = self.db.access_codes.insert({
                'code': '1234',
                'user': 'user1',
                }, safe=True)
        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid user
        self.assertRaises(HTTPUnauthorized, authorize_user, request)

        user_id = self.db.users.insert({
                'username': 'user1',
                }, safe=True)
        self.db.access_codes.update({'_id': access_code_id}, {
                '$set': {'user': user_id},
                }, safe=True)
        request = testing.FakeRequest(headers={
                'Authorization': 'Bearer 1234',
                }, db=self.db)
        # Invalid user
        authorized_user = authorize_user(request)
        self.assertEqual(authorized_user['username'], 'user1')
