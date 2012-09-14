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
        # See http://www.mongodb.org/display/DOCS/getLastError+Command#getLastErrorCommand-ReturnValue
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
        return result['n'] == 1
