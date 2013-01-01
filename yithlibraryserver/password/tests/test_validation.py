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

from yithlibraryserver.password.validation import validate_password


class UtilsTests(unittest.TestCase):

    def test_validate_password(self):
        # empty json
        password, errors = validate_password(b'')
        self.assertEqual(password, {})
        self.assertEqual(errors, ['No JSON object could be decoded'])

        # bad json
        password, errors = validate_password(b'[1')
        self.assertEqual(password, {})
        self.assertEqual(errors, ['No JSON object could be decoded'])

        # id not in the URL
        password, errors = validate_password(b'{}', _id='1')
        self.assertEqual(errors, ['The password id must be in the body',
                                  'Secret is required',
                                  'Service is required'])

        # id doesn't match URL's id
        password, errors = validate_password(b'{"_id": "1"}', _id='2')
        self.assertEqual(errors, ['The password id does not match the URL',
                                  'Secret is required',
                                  'Service is required'])

        # secret is missing
        password, errors = validate_password(b'{"_id": "1"}', _id='1')
        self.assertEqual(errors, ['Secret is required',
                                  'Service is required'])

        # service is missing
        password, errors = validate_password(b'{"_id": "1", "secret": "s3cr3t"}', _id='1')
        self.assertEqual(errors, ['Service is required'])

        # everything is fine
        password, errors = validate_password(b'{"_id": "1", "secret": "s3cr3t", "service": "myservice"}', _id='1')
        self.assertEqual(errors, [])
        self.assertEqual(password, {
                '_id': '1',
                'secret': 's3cr3t',
                'service': 'myservice',
                'account': None,
                'expiration': None,
                'notes': None,
                'tags': None,
                'creation': None,
                'last_modification': None,
                })
