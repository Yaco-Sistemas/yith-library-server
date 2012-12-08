# Yith Library Server is a password storage server.
# Copyright (C) 2012 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

from yithlibraryserver.user.models import User


class UserTests(unittest.TestCase):

    def test_unicode(self):
        data = {'_id': '1234'}
        self.assertEqual(unicode(User(data)), '1234')

        data['email'] = 'john@example.com'
        self.assertEqual(unicode(User(data)), 'john@example.com')

        data['last_name'] = 'Doe'
        self.assertEqual(unicode(User(data)), 'Doe')

        data['first_name'] = 'John'
        self.assertEqual(unicode(User(data)), 'John Doe')

        data['screen_name'] = 'Johnny'
        self.assertEqual(unicode(User(data)), 'Johnny')