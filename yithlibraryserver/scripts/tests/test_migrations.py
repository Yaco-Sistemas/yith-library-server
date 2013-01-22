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
from yithlibraryserver.scripts.migrations import migrate
from yithlibraryserver.scripts.testing import ScriptTests


class MigrationsTests(ScriptTests):

    clean_collections = ('users', 'passwords', 'applications')

    def test_migrate_add_send_email_preference(self):
        # Save sys values
        old_args = sys.argv[:]
        old_stdout = sys.stdout

        # Replace sys argv and stdout
        sys.argv = []
        sys.stdout = StringIO()

        # Call migrate with no arguments
        result = migrate()
        self.assertEqual(result, 2)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, 'You must provide two arguments. The first one is the config file and the second one is the migration name.\n')

        # Call migrate with a config file but no migration name
        sys.argv = ['notused', self.conf_file_path]
        sys.stdout = StringIO()
        result = migrate()
        self.assertEqual(result, 2)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, 'You must provide two arguments. The first one is the config file and the second one is the migration name.\n')

        # Call migrate with a config file and wrong migration name
        sys.argv = ['notused', self.conf_file_path, 'bad_migration']
        sys.stdout = StringIO()
        result = migrate()
        self.assertEqual(result, 3)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, 'The migration "bad_migration" does not exist.\n')

        # Good call
        sys.argv = ['notused', self.conf_file_path, 'add_send_email_preference']
        sys.stdout = StringIO()
        result = migrate()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        self.assertEqual(stdout, '')

        # Add some users
        u1_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                })
        self.db.users.insert({
                'first_name': 'John2',
                'last_name': 'Doe2',
                'email': 'john2@example.com',
                'send_passwords_periodically': False,
                })
        sys.argv = ['notused', self.conf_file_path, 'add_send_email_preference']
        sys.stdout = StringIO()
        result = migrate()
        self.assertEqual(result, None)
        stdout = sys.stdout.getvalue()
        expected_output = """Adding attribute "send_passwords_periodically" to John Doe <john@example.com>
"""
        self.assertEqual(stdout, expected_output)

        user1 = self.db.users.find_one({'_id': u1_id})
        self.assertEqual(user1['send_passwords_periodically'], True)

        # Restore sys.values
        sys.argv = old_args
        sys.stdout = old_stdout
