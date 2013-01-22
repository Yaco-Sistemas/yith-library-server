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

import optparse
import textwrap
import sys

from pyramid.paster import bootstrap

from yithlibraryserver.scripts.utils import safe_print
from yithlibraryserver.scripts.utils import get_user_display_name

migration_registry = {}

def migration(fnc):
    migration_registry[fnc.__name__] = fnc
    return fnc


def add_attribute(collection, obj, obj_repr, attribute, value):
    if attribute not in obj:
        safe_print('Adding attribute "%s" to %s' % (attribute, obj_repr))
        collection.update(
            {'_id': obj['_id']},
            {'$set': {attribute: value}},
            safe=True,
            )


@migration
def add_send_email_preference(db):
    for user in db.users.find():
        add_attribute(db.users, user, get_user_display_name(user),
                      'send_passwords_periodically', True)


def migrate():
    usage = "migrate: %prog config_uri migration_name"
    description = "Add a 'send_email_periodically' preference to every user."
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if len(args) != 2:
        safe_print('You must provide two arguments. '
                   'The first one is the config file and the '
                   'second one is the migration name.')
        return 2
    config_uri = args[0]
    migration_name = args[1]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    try:
        db = settings['mongodb'].get_database()

        if migration_name in migration_registry:
            migration = migration_registry[migration_name]
            migration(db)
        else:
            safe_print('The migration "%s" does not exist.' % migration_name)
            return 3
    finally:
        closer()
