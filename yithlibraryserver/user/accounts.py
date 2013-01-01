# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
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

import bson

from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


def get_available_providers():
    return ('facebook', 'google', 'twitter', 'persona')


def get_providers(user, current):
    result = []
    for provider in get_available_providers():
        key = provider + '_id'
        if key in user and user[key] is not None:
            result.append({
                    'name': provider,
                    'is_current': current == provider,
                    })
    return result


def get_n_passwords(db, user):
    return db.passwords.find({
            'owner': user.get('_id', None),
            }, safe=True).count()


def get_accounts(db, current_user, current_provider):
    email = current_user.get('email', None)
    results = db.users.find({
            'email': email,
            '_id': {'$ne': current_user.get('_id', None)},
            }, safe=True)

    if current_user:
        results = [current_user] + list(results)

    accounts = []
    for user in results:
        providers = get_providers(user, current_provider)
        is_current = current_provider in [p['name'] for p in providers]
        accounts.append({
            'providers': providers,
            'is_current': is_current,
            'passwords': get_n_passwords(db, user),
            'id': str(user['_id']),
            'is_verified': user.get('email_verified', False),
            })
    return accounts


def merge_accounts(db, master_user, accounts):
    merged = 0

    for account in accounts:
        user_id = bson.ObjectId(account)
        if master_user['_id'] == user_id:
            continue

        current_user = db.users.find_one({'_id': user_id}, safe=True)
        if current_user is None:
            continue

        merge_users(db, master_user, current_user)

        merged += 1

    return merged


def merge_users(db, user1, user2):
    # move all passwords of user2 to user1
    db.passwords.update({'owner': user2['_id']}, {
            '$set': {
                'owner': user1['_id'],
                },
            }, multi=True, safe=True)

    # copy authorized_apps from user2 to user1
    updates = {
        '$addToSet': {
            'authorized_apps': {
                '$each': user2['authorized_apps'],
                },
            },
        }

    # copy the providers
    for provider in get_available_providers():
        key = provider + '_id'
        if key in user2 and key not in user1:
            sets = updates.setdefault('$set', {})
            sets[key] = user2[key]

    db.users.update({'_id': user1['_id']}, updates, safe=True)

    # remove user2
    db.users.remove(user2['_id'])


def notify_admins_of_account_removal(request, user, reason, admin_emails):
    home_link = request.route_url('home')
    reason = reason or 'no reason was given'

    text_body = render(
        'yithlibraryserver.user:templates/account_removal_notification.txt',
        {'reason': reason, 'user': user, 'home_link': home_link},
        request=request,
        )
    # chamaleon txt templates are rendered as utf-8 bytestrings
    text_body = text_body.decode('utf-8')

    html_body = render(
        'yithlibraryserver.user:templates/account_removal_notification.pt',
        {'reason': reason, 'user': user, 'home_link': home_link},
        request=request,
        )

    message = Message(subject='A user has destroyed his Yith Library account',
                      recipients=admin_emails,
                      body=text_body,
                      html=html_body)
    get_mailer(request).send(message)
