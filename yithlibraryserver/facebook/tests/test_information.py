import unittest
from mock import patch

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.facebook.information import get_user_info


class InformationTests(unittest.TestCase):

    def test_get_user_info(self):
        settings = {
            'facebook_app_id': 'id',
            'facebook_secret': 'secret',
            'facebook_basic_information_url': 'https://graph.facebook.com/me'
            }

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 200
            response.json = {'first_name': 'John',
                             'last_name': 'Doe',
                             'email': 'john@example.com'}

            info = get_user_info(settings, 'token')
            self.assertEqual(info, {'first_name': 'John',
                                    'last_name': 'Doe',
                                    'email': 'john@example.com'})

        with patch('requests.get') as fake:
            response = fake.return_value
            response.status_code = 400
            response.json = {}

            self.assertRaises(HTTPUnauthorized,
                              get_user_info, settings, 'token')
