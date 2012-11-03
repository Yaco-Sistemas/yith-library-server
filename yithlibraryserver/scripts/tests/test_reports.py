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

import os
import sys
import tempfile
import unittest

from yithlibraryserver.db import MongoDB
from yithlibraryserver.compat import StringIO
from yithlibraryserver.testing import MONGO_URI
from yithlibraryserver.scripts.reports import usage

CONFIG = """[app:main]
use = egg:yith-library-server
mongo_uri = %s
testing = True

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 65432
""" % MONGO_URI


class ReportTests(unittest.TestCase):

    def setUp(self):
        fd, self.conf_file_path = tempfile.mkstemp()
        os.write(fd, CONFIG.encode('ascii'))
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        os.unlink(self.conf_file_path)
        self.db.drop_collection('users')
        self.db.drop_collection('passwords')

    def test_usage(self):
        # Save sys values
        old_args = sys.argv[:]
        old_stdout = sys.stdout

        # Replace sys argv and stdout
        sys.argv = []
        sys.stdout = StringIO('')

        # Call usage with no arguments
        result = usage()
        self.assertEqual(result, 2)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, 'You must provide at least one argument\n')

        # Call usage with a config file but an empty database
        sys.argv = ['notused', self.conf_file_path]
        sys.stdout = StringIO()
        result = usage()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, '')

        # Add some data to the database
        u1_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                })
        u2_id = self.db.users.insert({
                'first_name': 'John2',
                'last_name': 'Doe2',
                'email': 'john2@example.com',
                'email_verified': True,
                'twitter_id': '1234',
                })
        self.db.passwords.insert({
                'service': 'service1',
                'secret': 's3cr3t',
                'owner': u2_id,
                })
        u3_id = self.db.users.insert({
                'first_name': 'John3',
                'last_name': 'Doe3',
                'email': 'john3@example.com',
                'email_verified': True,
                'twitter_id': '1234',
                'facebook_id': '5678',
                'google_id': 'abcd',
                })
        self.db.passwords.insert({
                'service': 'service1',
                'secret': 's3cr3t',
                'owner': u3_id,
                })
        self.db.passwords.insert({
                'service': 'service2',
                'secret': 's3cr3t',
                'owner': u3_id,
                })
        sys.argv = ['notused', self.conf_file_path]
        sys.stdout = StringIO()
        result = usage()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        expected_output = """John Doe <john@example.com> (%s)
	Passwords: 0
	Providers: 
	Verified: False

John2 Doe2 <john2@example.com> (%s)
	Passwords: 1
	Providers: twitter
	Verified: True

John3 Doe3 <john3@example.com> (%s)
	Passwords: 2
	Providers: facebook, google, twitter
	Verified: True

""" % (u1_id, u2_id, u3_id)
        self.assertEqual(stdout, expected_output)

        # Restore sys.values
        sys.argv = old_args
        sys.stdout = old_stdout
