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

import unittest

from yithlibraryserver import db


class FakeDatabase(object):

    def __init__(self, name):
        self.name = name
        self.is_authenticated = False

    def authenticate(self, user, password):
        self.is_authenticated = True


class FakeConnection(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __getitem__(self, key):
        return FakeDatabase(key)


class MongoDBTests(unittest.TestCase):

    def test_uri(self):
        mdb = db.MongoDB(connection_factory=FakeConnection)

        self.assertEqual(mdb.db_uri.geturl(), db.DEFAULT_MONGODB_URI)
        self.assertEqual(mdb.database_name, db.DEFAULT_MONGODB_NAME)
        database = mdb.get_database()
        self.assertTrue(isinstance(database, FakeDatabase))
        self.assertEqual(database.name, mdb.database_name)
        self.assertFalse(database.is_authenticated)

        # full specified uri
        uri = 'mongodb://db.example.com:1111/testdb'
        mdb = db.MongoDB(uri, connection_factory=FakeConnection)
        conn = mdb.get_connection()
        database = mdb.get_database()
        self.assertEqual(mdb.db_uri.geturl(), uri)
        self.assertEqual(mdb.db_uri.hostname, 'db.example.com')
        self.assertEqual(conn.kwargs['host'], 'db.example.com')
        self.assertEqual(mdb.db_uri.port, 1111)
        self.assertEqual(conn.kwargs['port'], 1111)
        self.assertEqual(mdb.database_name, 'testdb')
        self.assertFalse(database.is_authenticated)

        # uri without path component
        uri = 'mongodb://db.example.com:1111'
        mdb = db.MongoDB(uri, connection_factory=FakeConnection)
        conn = mdb.get_connection()
        database = mdb.get_database()
        self.assertEqual(mdb.db_uri.geturl(), uri)
        self.assertEqual(mdb.db_uri.hostname, 'db.example.com')
        self.assertEqual(conn.kwargs['host'], 'db.example.com')
        self.assertEqual(mdb.db_uri.port, 1111)
        self.assertEqual(conn.kwargs['port'], 1111)
        self.assertEqual(mdb.database_name, db.DEFAULT_MONGODB_NAME)
        self.assertFalse(database.is_authenticated)

        # uri without port
        uri = 'mongodb://db.example.com'
        mdb = db.MongoDB(uri, connection_factory=FakeConnection)
        conn = mdb.get_connection()
        self.assertEqual(mdb.db_uri.geturl(), uri)
        self.assertEqual(mdb.db_uri.hostname, 'db.example.com')
        self.assertEqual(conn.kwargs['host'], 'db.example.com')
        self.assertEqual(mdb.db_uri.port, None)
        self.assertEqual(conn.kwargs['port'], db.DEFAULT_MONGODB_PORT)
        self.assertEqual(mdb.database_name, db.DEFAULT_MONGODB_NAME)
        self.assertFalse(database.is_authenticated)

        # uri without anything
        uri = 'mongodb://'
        mdb = db.MongoDB(uri, connection_factory=FakeConnection)
        conn = mdb.get_connection()
        database = mdb.get_database()
        self.assertEqual(mdb.db_uri.geturl(), 'mongodb:')
        self.assertEqual(mdb.db_uri.hostname, None)
        self.assertEqual(conn.kwargs['host'], db.DEFAULT_MONGODB_HOST)
        self.assertEqual(mdb.db_uri.port, None)
        self.assertEqual(conn.kwargs['port'], db.DEFAULT_MONGODB_PORT)
        self.assertEqual(mdb.database_name, db.DEFAULT_MONGODB_NAME)
        self.assertFalse(database.is_authenticated)

        # uri with username and password
        uri = 'mongodb://john:secret@db.example.com:1111/testdb'
        mdb = db.MongoDB(uri, connection_factory=FakeConnection)
        conn = mdb.get_connection()
        database = mdb.get_database()
        self.assertEqual(mdb.db_uri.geturl(), uri)
        self.assertEqual(mdb.db_uri.hostname, 'db.example.com')
        self.assertEqual(conn.kwargs['host'], 'db.example.com')
        self.assertEqual(mdb.db_uri.port, 1111)
        self.assertEqual(conn.kwargs['port'], 1111)
        self.assertEqual(mdb.database_name, 'testdb')
        self.assertTrue(database.is_authenticated)
