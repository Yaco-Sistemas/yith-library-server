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

from yithlibraryserver.password.models import PasswordsManager
from yithlibraryserver.utils import remove_attrs


def get_user_passwords(db, user):
    passwords_manager = PasswordsManager(db)
    return [remove_attrs(password, 'owner', '_id')
            for password in passwords_manager.retrieve(user)]


def get_backup_filename():
    today = datetime.date.today()
    return 'yith-library-backup-%d-%02d-%02d.json' % (
        today.year, today.month, today.day)