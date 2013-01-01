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


class PasswordsManager(object):

    def __init__(self, db):
        self.db = db

    def create(self, user, password):
        """Creates and returns a new password.

        Stores the password in the database for this specific user
        and returns a new dict with the 'owner' and '_id' fields
        filled.
        """
        new_password = dict(password)  # copy since we are changing this object
        new_password['owner'] = user['_id']
        _id = self.db.passwords.insert(new_password, safe=True)
        new_password['_id'] = _id
        return new_password

    def retrieve(self, user, _id=None):
        """Return the user's passwords or just one.

        If _id is None return the whole set of passwords for this
        user. Otherwise, it returns the password with that _id.
        """
        if _id is None:
            return self.db.passwords.find({'owner': user['_id']})
        else:
            return self.db.passwords.find_one({
                    '_id': _id,
                    'owner': user['_id'],
                    })

    def update(self, user, _id, password):
        """Update a password in the database.

        Return the updated password on success or None if the original
        password does not exist.
        """
        new_password = dict(password)  # copy since we are changing this object
        new_password['owner'] = user['_id']
        result = self.db.passwords.update({
                '_id': _id,
                'owner': user['_id'],
                }, new_password, safe=True)
        new_password['_id'] = _id

        # result['n'] is the number of documents updated
        # See <http://www.mongodb.org/display/DOCS/getLastError+Command#getLastErrorCommand-ReturnValue
        if result['n'] == 1:
            return new_password
        else:
            return None

    def delete(self, user, _id=None):
        """Deletes a password from the database or the whole set for this user.

        Returns True if the delete is succesfull or False otherwise.
        """
        query = {'owner': user['_id']}
        if _id is not None:
            query['_id'] = _id

        result = self.db.passwords.remove(query, safe=True)
        return result['n'] > 0
