from yithlibraryserver import testing


class ViewTests(testing.ViewTests):

    def test_authorization_endpoint(self):
        res = self.testapp.get('/oauth2/endpoints/authorization',
                               status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required response_type')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'token',
                }, status=501)

        self.assertEqual(res.status, '501 Not Implemented')
        res.mustcontain('Only code is supported')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')
        res.mustcontain('Missing required client_type')

        res = self.testapp.get('/oauth2/endpoints/authorization', {
                'response_type': 'code',
                'client_id': '1234',
                }, status=404)
        self.assertEqual(res.status, '404 Not Found')
