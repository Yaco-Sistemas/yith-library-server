# Yith Library Server is a password storage server.
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

import optparse
import textwrap
import sys

from pyramid.paster import bootstrap

from yithlibraryserver.user.accounts import get_available_providers
from yithlibraryserver.user.accounts import get_n_passwords


def _get_user_display_name(user):
    return '%s %s <%s>' % (user.get('first_name', ''),
                           user.get('last_name', ''),
                           user.get('email', ''))


def _get_user_info(db, user):
    return {
        'display_name': _get_user_display_name(user),
        'passwords': get_n_passwords(db, user),
        'providers': ', '.join([prov for prov in get_available_providers()
                                if ('%s_id' % prov) in user]),
        'verified': user.get('email_verified', False),
        'date_joined': user.get('date_joined', 'Unknown'),
        'last_login': user.get('last_login', 'Unknown'),
        }


def usage():
    description = "Report information about users and their passwords."
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
                  '\tVerified: %s\n'
                  '\tDate joined: %s\n'
                  '\tLast login: %s\n' % (
                    info['display_name'], user['_id'],
                    info['passwords'], info['providers'], info['verified'],
                    info['date_joined'], info['last_login'],
                    ))

    finally:
        closer()


def _get_app_info(db, app):
    user = db.users.find_one({'_id': app['owner']})
    if user is None:
        owner = 'Unknown owner (%s)' % app['owner']
    else:
        owner = _get_user_display_name(user)

    return {
        'name': app['name'],
        'owner': owner,
        'main_url': app['main_url'],
        'callback_url': app['callback_url'],
        'users': db.users.find({
                'authorized_apps': {'$in': [app['_id']]},
                }).count()
        }


def applications():
    description = "Report information about oauth2 client applications."
    usage = "applications: %prog config_uri"
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
        for app in db.applications.find():
            info = _get_app_info(db, app)
            print('%s\n'
                  '\tOwner: %s\n'
                  '\tMain URL: %s\n'
                  '\tCallback URL: %s\n'
                  '\tUsers: %d\n' % (
                    info['name'], info['owner'],
                    info['main_url'], info['callback_url'],
                    info['users'],
                    ))

    finally:
        closer()
