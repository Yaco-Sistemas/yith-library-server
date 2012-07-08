from urllib.parse import urlparse

import pymongo


DEFAULT_MONGODB_HOST = 'localhost'
DEFAULT_MONGODB_PORT = '27017'
DEFAULT_MONGODB_NAME = 'yith-library'
DEFAULT_MONGODB_URI = 'mongodb://%s:%s/%s' % (DEFAULT_MONGODB_HOST,
                                              DEFAULT_MONGODB_PORT,
                                              DEFAULT_MONGODB_NAME)


class MongoDB(object):
    """Simple wrapper to get pymongo real objects from the settings uri"""

    def __init__(self, db_uri=DEFAULT_MONGODB_URI,
                 connection_factory=pymongo.Connection):
        self.db_uri = urlparse(db_uri)
        self.connection = connection_factory(
            host=self.db_uri.hostname or DEFAULT_MONGODB_HOST,
            port=self.db_uri.port or DEFAULT_MONGODB_PORT)

        if self.db_uri.path:
            self.database_name = self.db_uri.path[1:]
        else:
            self.database_name = DEFAULT_MONGODB_NAME

    def get_connection(self):
        return self.connection

    def get_database(self):
        database = self.connection[self.database_name]
        if self.db_uri.username and self.db_uri.password:
            database.authenticate(self.db_uri.username, self.db_uri.password)

        return database
