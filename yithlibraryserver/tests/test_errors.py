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

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound


from yithlibraryserver.errors import password_not_found, invalid_password_id


class ErrorsTests(unittest.TestCase):

    def test_password_not_found(self):
        result = password_not_found()
        self.assertTrue(isinstance(result, HTTPNotFound))
        self.assertTrue(result.content_type, 'application/json')
        self.assertTrue(result.body, '{"message": "Password not found"}')

        # try a different message
        result = password_not_found('test')
        self.assertTrue(result.body, '{"message": "test"}')


    def test_invalid_password_id(self):
        result = invalid_password_id()
        self.assertTrue(isinstance(result, HTTPBadRequest))
        self.assertTrue(result.content_type, 'application/json')
        self.assertTrue(result.body, '{"message": "Invalid password id"}')

        # try a different message
        result = invalid_password_id('test')
        self.assertTrue(result.body, '{"message": "test"}')
