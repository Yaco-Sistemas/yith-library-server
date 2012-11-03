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

import optparse
import textwrap
import sys

from pyramid.paster import bootstrap

from yithlibraryserver.user.accounts import get_available_providers
from yithlibraryserver.user.accounts import get_n_passwords


def _get_user_info(db, user):
    return {
        'display_name': '%s %s <%s>' % (
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('email', '')),
        'passwords': get_n_passwords(db, user),
        'providers': ', '.join([prov for prov in get_available_providers()
                                if ('%s_id' % prov) in user]),
        'verified': user.get('email_verified', False),
        }


def usage():
    description = "Report users and their password number."
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    try:
        db = settings['mongodb'].get_database()
        for user in db.users.find():
            info = _get_user_info(db, user)
            print('%s (%s)\n'
                  '\tPasswords: %d\n'
                  '\tProviders: %s\n'
                  '\tVerified: %s\n' % (
                    info['display_name'], user['_id'],
                    info['passwords'], info['providers'], info['verified'],
                    ))

    finally:
        closer()
