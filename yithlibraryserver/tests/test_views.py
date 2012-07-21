from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    def test_home(self):
        res = self.testapp.get('/')
        self.assertEqual(res.status, '200 OK')
