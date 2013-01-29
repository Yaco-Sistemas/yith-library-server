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

import sys

from yithlibraryserver.compat import StringIO
from yithlibraryserver.scripts.announce import announce
from yithlibraryserver.scripts.testing import ScriptTests


class AnnounceTests(ScriptTests):

    clean_collections = ('users', 'passwords')

    def setUp(self):
        super(AnnounceTests, self).setUp()
        # Save sys values
        self.old_args = sys.argv[:]
        self.old_stdout = sys.stdout

    def tearDown(self):
        # Restore sys.values
        sys.argv = self.old_args
        sys.stdout = self.old_stdout
        super(AnnounceTests, self).tearDown()

    def test_no_arguments(self):
        sys.argv = []
        sys.stdout = StringIO()

        result = announce()
        self.assertEqual(result, 2)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, 'You must provide two arguments. The first one is the config file and the second one is the email template.\n')

    def test_empty_database(self):
        sys.argv = ['notused', self.conf_file_path, 'new_feature_send_passwords_via_email']
        sys.stdout = StringIO()
        result = announce()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, '')

    def test_announce_send_email(self):
        self.add_passwords(self.db.users.insert({
                    'first_name': 'John1',
                    'last_name': 'Doe',
                    'email': '',
                    'send_passwords_periodically': False,
                    }), 10)
        self.add_passwords(self.db.users.insert({
                    'first_name': 'John2',
                    'last_name': 'Doe',
                    'email': 'john2@example.com',
                    'send_passwords_periodically': False,
                    }), 10)
        self.add_passwords(self.db.users.insert({
                    'first_name': 'John3',
                    'last_name': 'Doe',
                    'email': 'john3@example.com',
                    'send_passwords_periodically': True,
                    }), 10)
        self.db.users.insert({
                    'first_name': 'John4',
                    'last_name': 'Doe',
                    'email': 'john4@example.com',
                    'send_passwords_periodically': True,
                    })

        sys.argv = ['notused', self.conf_file_path, 'new_feature_send_passwords_via_email']
        sys.stdout = StringIO()
        result = announce()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        expected_output = """Sending email to John2 Doe <john2@example.com>
Sending email to John3 Doe <john3@example.com>
"""
        self.assertEqual(stdout, expected_output)
