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
            'twitter_consumer_key': 'key',
            'twitter_consumer_secret': 'secret',
            'facebook_app_id': 'id',
            'facebook_app_secret': 'secret',
            'testing': True,
            'admin_emails': 'admin1@example.com admin2@example.com'
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
        session_factory = self.testapp.app.registry.queryUtility(ISessionFactory)
        request = DummyRequest()
        session = session_factory(request)
        for key, value in data.items():
            session[key] = value
        session.persist()
        self.testapp.cookies['beaker.session.id'] = session._sess.id
