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
