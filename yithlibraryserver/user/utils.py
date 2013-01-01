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
import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember


def split_name(name):
    parts = name.split(' ')
    if len(parts) > 1:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = parts[0]
        last_name = ''

    return first_name, last_name


def delete_user(db, user):
    result = db.users.remove(user['_id'], safe=True)
    return result['n'] == 1


def update_user(db, user, user_info, other_changes):
    changes = {}
    for attribute in ('screen_name', 'first_name', 'last_name', 'email'):
        if attribute in user_info and user_info[attribute]:
            if attribute in user:
                if user_info[attribute] != user[attribute]:

                    changes[attribute] = user_info[attribute]
            else:
                changes[attribute] = user_info[attribute]

    changes.update(other_changes)

    db.users.update({'_id': user['_id']}, {'$set': changes}, safe=True)


def _get_provider_key(provider):
    return '%s_id' % provider


def user_from_provider_id(db, provider, user_id):
    provider_key = _get_provider_key(provider)
    return db.users.find_one({provider_key: user_id})


def register_or_update(request, provider, user_id, info, default_url='/'):
    provider_key = _get_provider_key(provider)
    user = user_from_provider_id(request.db, provider, user_id)
    if user is None:

        new_info = {'provider': provider, provider_key: user_id}
        for attribute in ('screen_name', 'first_name', 'last_name', 'email'):
            if attribute in info:
                new_info[attribute] = info[attribute]
            else:
                new_info[attribute] = ''

        request.session['user_info'] = new_info
        if 'next_url' not in request.session:
            request.session['next_url'] = default_url
        return HTTPFound(location=request.route_path('register_new_user'))
    else:
        changes = {'last_login': datetime.datetime.utcnow()}

        ga = request.google_analytics
        if ga.is_in_session():
            if not ga.is_stored_in_user(user):
                changes.update(ga.get_user_attr(ga.show_in_session()))
            ga.clean_session()

        update_user(request.db, user, info, changes)

        if 'next_url' in request.session:
            next_url = request.session['next_url']
            del request.session['next_url']
        else:
            next_url = default_url

        request.session['current_provider'] = provider
        remember_headers = remember(request, str(user['_id']))
        return HTTPFound(location=next_url, headers=remember_headers)
