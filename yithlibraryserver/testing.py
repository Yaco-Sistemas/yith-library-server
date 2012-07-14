import unittest

from webtest import TestApp

from yithlibraryserver import main


class ViewTests(unittest.TestCase):

    def setUp(self):
        app = main({}, mongo_uri='mongodb://localhost:27017/test-yith-library')
        self.testapp = TestApp(app)
        self.db = app.registry.settings['db_conn']['test-yith-library']
