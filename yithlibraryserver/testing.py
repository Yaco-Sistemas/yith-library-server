import unittest

from webtest import TestApp, TestRequest

from pyramid.security import remember

from yithlibraryserver import main


class FakeRequest(object):

    def __init__(self, headers, db=None):
        self.headers = headers
        self.authorization = headers.get('Authorization', '').split(' ')
        self.db = db


class TestCase(unittest.TestCase):

    clean_collections = tuple()

    def setUp(self):
        app = main({}, mongo_uri='mongodb://localhost:27017/test-yith-library')
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
