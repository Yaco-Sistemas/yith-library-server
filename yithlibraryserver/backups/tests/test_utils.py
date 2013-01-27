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

import datetime

from yithlibraryserver.backups.utils import get_user_passwords
from yithlibraryserver.backups.utils import get_backup_filename
from yithlibraryserver.backups.utils import compress, uncompress
from yithlibraryserver.testing import TestCase


class UtilsTests(TestCase):

    clean_collections = ('users', 'passwords', )

    def test_get_user_passwords(self):
        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id})

        self.assertEqual(get_user_passwords(self.db, user), [])

        self.db.passwords.insert({
                'owner': user_id,
                'password': 'secret1',
                })
        self.db.passwords.insert({
                'owner': user_id,
                'password': 'secret2',
                })

        self.assertEqual(get_user_passwords(self.db, user), [{
                    'password': 'secret1',
                    } ,{
                    'password': 'secret2',
                    }])

    def test_get_backup_filename(self):
        self.assertEqual(get_backup_filename(datetime.date(2012, 10, 28)),
                         'yith-library-backup-2012-10-28.yith')
        self.assertEqual(get_backup_filename(datetime.date(2013, 1, 8)),
                         'yith-library-backup-2013-01-08.yith')

    def test_compress_and_uncompress(self):
        passwords = [{'password': 'secret1'}, {'password': 'secret2'}]

        self.assertEqual(uncompress(compress(passwords)), passwords)
