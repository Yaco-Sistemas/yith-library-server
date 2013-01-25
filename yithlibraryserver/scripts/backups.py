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

import transaction

from yithlibraryserver.backups.email import send_passwords
from yithlibraryserver.scripts.utils import safe_print, setup_simple_command
from yithlibraryserver.scripts.utils import get_user_display_name


def get_all_users(db):
    return db.users.find({
            'send_passwords_periodically': True,
            }).sort('date_joined')


def get_selected_users(db, *emails):
    for email in emails:
        for user in db.users.find({
                'email': email,
                }).sort('date_joined'):
            yield user


def send_backups_via_email():
    result = setup_simple_command(
        "users",
        "Report information about users and their passwords.",
        )
    if isinstance(result, int):
        return result
    else:
        settings, closer, env, args = result

    try:

        db = settings['mongodb'].get_database()
        request = env['request']

        if len(args) == 0:
            user_iterator = get_all_users(db)
        else:
            user_iterator = get_selected_users(db, *args)

        tx = transaction.begin()

        for user in user_iterator:
            if user['email']:
                sent = send_passwords(request, user)
                if sent:
                    safe_print('Passwords sent to %s' %
                               get_user_display_name(user))

        tx.commit()

    finally:
        closer()
