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

from webtest import TestApp, TestRequest

from pyramid.interfaces import ISessionFactory
from pyramid.security import remember
from pyramid.testing import DummyRequest

from yithlibraryserver import main

MONGO_URI = 'mongodb://localhost:27017/test-yith-library'


class FakeRequest(DummyRequest):

    def __init__(self, *args, **kwargs):
        super(FakeRequest, self).__init__(*args, **kwargs)
        self.authorization = self.headers.get('Authorization', '').split(' ')
        if 'db' in kwargs:
            self.db = kwargs['db']


class TestCase(unittest.TestCase):

    clean_collections = tuple()

    def setUp(self):
        settings = {
            'mongo_uri': MONGO_URI,
            'auth_tk_secret': '123456',
            'twitter_consumer_key': 'key',
            'twitter_consumer_secret': 'secret',
            'facebook_app_id': 'id',
            'facebook_app_secret': 'secret',
            'google_client_id': 'id',
            'google_client_secret': 'secret',
            'testing': True,
            'admin_emails': 'admin1@example.com admin2@example.com',
            'persona_audience': 'https//localhost:6543',
            }
        app = main({}, **settings)
        self.testapp = TestApp(app)
        self.db = app.registry.settings['db_conn']['test-yith-library']

    def tearDown(self):
        for col in self.clean_collections:
            self.db.drop_collection(col)

        self.testapp.reset()

    def set_user_cookie(self, user_id):
        request = TestRequest.blank('', {})
        request.registry = self.testapp.app.registry
        remember_headers = remember(request, user_id)
        cookie_value = remember_headers[0][1].split('"')[1]
        self.testapp.cookies['auth_tkt'] = cookie_value

    def add_to_session(self, data):
        queryUtility = self.testapp.app.registry.queryUtility
        session_factory = queryUtility(ISessionFactory)
        request = DummyRequest()
        session = session_factory(request)
        for key, value in data.items():
            session[key] = value
        session.persist()
        self.testapp.cookies['beaker.session.id'] = session._sess.id

    def get_session(self, response):
        queryUtility = self.testapp.app.registry.queryUtility
        session_factory = queryUtility(ISessionFactory)
        request = response.request

        if not hasattr(request, 'add_response_callback'):
            request.add_response_callback = lambda r: r

        if 'Set-Cookie' in response.headers:
            request.environ['HTTP_COOKIE'] = response.headers['Set-Cookie']

        return session_factory(request)
