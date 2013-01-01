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

import uuid


class Codes(object):

    collection_name = ''

    def __init__(self, db):
        self.db = db
        self.collection = self.db[self.collection_name]

    def create(self, user_id, **kwargs):
        code = str(uuid.uuid4())

        new_obj = {
            'code': code,
            'user': user_id,
            }
        new_obj.update(kwargs)

        old_obj = dict(kwargs)  # make a copy
        old_obj['user'] = user_id

        self.collection.remove(old_obj, safe=True)
        self.collection.insert(new_obj, safe=True)

        return code

    def find(self, code):
        return self.collection.find_one({'code': code})

    def remove(self, code_obj):
        self.collection.remove(code_obj, safe=True)


class AuthorizationCodes(Codes):

    collection_name = 'authorization_codes'

    def get_redirect_url(self, code, uri, state=None):
        parameters = ['code=%s' % code]
        if state:
            parameters.append('state=%s' % state)
        return '%s?%s' % (uri, '&'.join(parameters))

    def create(self, user_id, client_id, scope):
        return super(AuthorizationCodes, self).create(user_id,
                                                      scope=scope,
                                                      client_id=client_id)


class AccessCodes(Codes):

    collection_name = 'access_codes'

    def create(self, user_id, grant):
        return super(AccessCodes, self).create(user_id,
                                               scope=grant['scope'],
                                               client_id=grant['client_id'])


class Authorizator(object):

    def __init__(self, db, app):
        self.db = db
        self.app = app
        self.auth_codes = AuthorizationCodes(db)
        self.access_codes = AccessCodes(db)

    def is_app_authorized(self, user):
        return self.app['_id'] in user['authorized_apps']

    def store_user_authorization(self, user):
        self.db.users.update(
            {'_id': user['_id']},
            {'$addToSet': {'authorized_apps': self.app['_id']}},
            safe=True,
            )

    def remove_user_authorization(self, user):
        self.db.users.update(
            {'_id': user['_id']},
            {'$pull': {'authorized_apps': self.app['_id']}},
            safe=True,
            )
