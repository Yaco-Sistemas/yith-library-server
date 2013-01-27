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

import os
import unittest
import tempfile

from yithlibraryserver.db import MongoDB
from yithlibraryserver.testing import MONGO_URI

CONFIG = """[app:main]
use = egg:yith-library-server
mongo_uri = %s
auth_tk_secret = 123456
testing = True
pyramid_mailer.prefix = mail_
mail_default_sender = no-reply@yithlibrary.com
admin_emails = admin1@example.com admin2@example.com

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 65432
""" % MONGO_URI


class ScriptTests(unittest.TestCase):

    clean_collections = tuple()

    def setUp(self):
        fd, self.conf_file_path = tempfile.mkstemp()
        os.write(fd, CONFIG.encode('ascii'))
        mdb = MongoDB(MONGO_URI)
        self.db = mdb.get_database()

    def tearDown(self):
        os.unlink(self.conf_file_path)
        for col in self.clean_collections:
            self.db.drop_collection(col)

    def add_passwords(self, user, n):
        for i in range(n):
            self.db.passwords.insert({
                    'service': 'service-%d' % (i + 1),
                    'secret': 's3cr3t',
                    'owner': user,
                    })
