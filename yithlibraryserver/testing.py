import unittest

from webtest import TestApp

from yithlibraryserver import main


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
