import unittest

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound


from yithlibraryserver.errors import password_not_found, invalid_password_id


class ErrorsTests(unittest.TestCase):

    def test_password_not_found(self):
        result = password_not_found()
        self.assertTrue(isinstance(result, HTTPNotFound))
        self.assertTrue(result.content_type, 'application/json')
        self.assertTrue(result.body, '{"message": "Password not found"}')

        # try a different message
        result = password_not_found('test')
        self.assertTrue(result.body, '{"message": "test"}')


    def test_invalid_password_id(self):
        result = invalid_password_id()
        self.assertTrue(isinstance(result, HTTPBadRequest))
        self.assertTrue(result.content_type, 'application/json')
        self.assertTrue(result.body, '{"message": "Invalid password id"}')

        # try a different message
        result = invalid_password_id('test')
        self.assertTrue(result.body, '{"message": "test"}')
