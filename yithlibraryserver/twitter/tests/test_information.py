import unittest
from mock import patch

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.twitter.information import get_user_info


class InformationTests(unittest.TestCase):

    def test_get_user_info(self):
        settings = {
            'twitter_consumer_key': 'key',
            'twitter_consumer_secret': 'secret',
            'twitter_user_info_url': 'https://api.twitter.com/1/users/show.json'
            }

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 200
            response.json = {'screen_name': 'John Doe'}

            info = get_user_info(settings, '1234', 'token')
            self.assertEqual(info, {'screen_name': 'John Doe'})

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 400
            response.json = {'screen_name': 'John Doe'}

            self.assertRaises(HTTPUnauthorized,
                              get_user_info, settings, '1234', 'token')
