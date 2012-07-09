import unittest

from yithlibraryserver.cors import CORSManager


class FakeRequest(object):

    def __init__(self, headers):
        self.headers = headers

FakeResponse = FakeRequest


class CORSManagerTests(unittest.TestCase):

    def test_cors_headers(self):
        cm = CORSManager('')

        request = FakeRequest({'Origin': 'foo'})
        response = FakeResponse({})

        cm.add_cors_header(request, response)

        self.assertEqual(response.headers, {})


        cm = CORSManager('http://localhost')

        request = FakeRequest({'Origin': 'http://localhost'})
        response = FakeResponse({})

        cm.add_cors_header(request, response)

        self.assertEqual(response.headers,
                         {'Access-Control-Allow-Origin': 'http://localhost'})
