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

import operator
import optparse
import textwrap
import sys

from pyramid.paster import bootstrap

from yithlibraryserver.compat import PY3
from yithlibraryserver.user.accounts import get_available_providers
from yithlibraryserver.user.accounts import get_provider_key, get_n_passwords


def safe_print(value):
    if PY3:
        print(value)
    else:
        print(value.encode('utf-8'))


def setup_simple_command(name, description):
    usage = name + ": %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        safe_print('You must provide at least one argument')
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    return settings, closer, env


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


def users():
    result = setup_simple_command(
        "users",
        "Report information about users and their passwords.",
        )
    if isinstance(result, int):
        return result
    else:
        settings, closer, env = result

    try:
        db = settings['mongodb'].get_database()
        for user in db.users.find().sort('date_joined'):
            info = _get_user_info(db, user)
            text = ('%s (%s)\n'
                    '\tPasswords: %d\n'
                    '\tProviders: %s\n'
                    '\tVerified: %s\n'
                    '\tDate joined: %s\n'
                    '\tLast login: %s\n' % (
                    info['display_name'], user['_id'],
                    info['passwords'], info['providers'], info['verified'],
                    info['date_joined'], info['last_login'],
                    ))
            safe_print(text)

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
    result = setup_simple_command(
        "applications",
        "Report information about oauth2 client applications.",
        )
    if isinstance(result, int):
        return result
    else:
        settings, closer, env = result

    try:
        db = settings['mongodb'].get_database()
        for app in db.applications.find():
            info = _get_app_info(db, app)
            text = ('%s\n'
                    '\tOwner: %s\n'
                    '\tMain URL: %s\n'
                    '\tCallback URL: %s\n'
                    '\tUsers: %d\n' % (
                    info['name'], info['owner'],
                    info['main_url'], info['callback_url'],
                    info['users'],
                    ))
            safe_print(text)

    finally:
        closer()


def group_by_identity_provider(users):
    providers = {}
    for user in users:
        for provider in get_available_providers():
            key = get_provider_key(provider)
            if user.get(key, None):
                if provider in providers:
                    providers[provider] += 1
                else:
                    providers[provider] = 1

    providers = providers.items()
    providers.sort(key=operator.itemgetter(1), reverse=True)
    return providers


def group_by_email_provider(users, threshold):
    providers = {}
    no_email = 0
    for user in users:
        email = user.get('email', None)
        if not email:
            no_email += 1
            continue

        provider = email.split('@')[1]
        if provider in providers:
            providers[provider] += 1
        else:
            providers[provider] = 1

    providers = [(p, a) for p, a in providers.items() if a > threshold]
    providers.sort(key=operator.itemgetter(1), reverse=True)

    return providers, no_email


def users_with_most_passwords(users, passwords, amount):
    # make a password dict keyed by users_id
    passwords_map = {}
    for password in passwords:
        owner = password['owner']
        if owner in passwords_map:
            passwords_map[owner] += 1
        else:
            passwords_map[owner] = 1

    users_map = dict([(user['_id'], user) for user in users])

    passwords_list = passwords_map.items()
    passwords_list.sort(key=operator.itemgetter(1), reverse=True)
    passwords_list = passwords_list[:amount]

    result = []
    for password_owner, amount in passwords_list:
        result.append((users_map[password_owner], amount))

    return result, len(passwords_map)


def statistics():
    result = setup_simple_command(
        "statistics",
        "Report several different statistics.",
        )
    if isinstance(result, int):
        return result
    else:
        settings, closer, env = result

    try:
        db = settings['mongodb'].get_database()

        # Get the number of users and passwords
        n_users = db.users.count()
        if n_users == 0:
            return

        n_passwords = db.passwords.count()

        # How many users are verified
        n_verified = db.users.find({'email_verified': True}).count()
        # How many users allow the analytics cookie
        n_allow_cookie = db.users.find({'allow_google_analytics': True}).count()

        all_users = list(db.users.find())

        # Identity providers
        by_identity = group_by_identity_provider(all_users)

        # Email providers
        by_email, without_email = group_by_email_provider(all_users, 1)
        with_email = n_users - without_email

        # Top ten users
        all_passwords = list(db.passwords.find())
        most_active_users, users_no_passwords = users_with_most_passwords(
            all_users, all_passwords, 10)

        # print the statistics
        safe_print('Number of users: %d' % n_users)
        safe_print('Number of passwords: %d' % n_passwords)
        safe_print('Verified users: %.2f%%' % ((100.0 * n_verified) / n_users))
        safe_print('Users that allow Google Analytics cookie: %.2f%%' % (
                (100.0 * n_allow_cookie) / n_users))

        safe_print('Identity providers:')
        for provider, amount in by_identity:
            safe_print('\t%s: %.2f%%' % (provider, (100.0 * amount) / n_users))

        safe_print('Email providers:')
        others = with_email
        for provider, amount in by_email:
            safe_print('\t%s: %.2f%%' % (provider, (100.0 * amount) / with_email))
            others -= amount
        safe_print('\tOthers: %.2f%%' % ((100.0 * others) / with_email))
        safe_print('Users without email: %d' % without_email)

        safe_print('Most active users:')
        for user, n_passwords in most_active_users:
            safe_print('\t%s: %s' % (_get_user_display_name(user), n_passwords))

        safe_print('Users without passwords: %d' %
                   (n_users - users_no_passwords))

    finally:
        closer()
