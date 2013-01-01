# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012-2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of Yith Library Server.
#
# Yith Library Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yith Library Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.

import time
import unittest


from yithlibraryserver.twitter.authorization import quote, nonce, timestamp
from yithlibraryserver.twitter.authorization import sign, auth_header

class AuthorizationTests(unittest.TestCase):

    def test_quote(self):
        self.assertEqual(quote('a test'), 'a%20test')
        self.assertEqual(quote('a/test'), 'a%2Ftest')

    def test_nonce(self):
        self.assertEqual(len(nonce()), 8)
        self.assertEqual(len(nonce(10)), 10)
        self.assertNotEqual(nonce(), nonce())

    def test_timestamp(self):
        t1 = timestamp()
        time.sleep(1)
        t2 = timestamp()
        self.assertTrue(t2 > t1)

    def test_sign(self):
        # this example is taken from
        # https://dev.twitter.com/docs/auth/creating-signature
        method = 'post'
        url = 'https://api.twitter.com/1/statuses/update.json'
        params = (
            ('status', quote('Hello Ladies + Gentlemen, a signed OAuth request!')),
            ('include_entities', quote('true')),
            ('oauth_consumer_key', quote('xvz1evFS4wEEPTGEFPHBog')),
            ('oauth_nonce', quote('kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg')),
            ('oauth_signature_method', quote('HMAC-SHA1')),
            ('oauth_timestamp', quote('1318622958')),
            ('oauth_token', quote('370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb')),
            ('oauth_version', quote('1.0')),
            )
        consumer_secret = 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw'
        oauth_token = 'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'

        self.assertEqual(sign(method, url, params,
                              consumer_secret, oauth_token),
                         quote('tnnArxj06cWHq44gCs1OSKk/jLY='))

    def test_auth_header(self):
        # this example is taken from
        # https://dev.twitter.com/docs/auth/implementing-sign-twitter
        settings = {
            'twitter_consumer_key': 'cChZNFj6T5R0TigYB9yd1w',
            'twitter_consumer_secret': 'L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg',
            }
        params = (
            ('oauth_callback', 'http://localhost/sign-in-with-twitter/'),
            )
        token = ''
        nc = 'ea9ec8429b68d6b77cd5600adbbb0456'
        ts = 1318467427
        res = auth_header('post', 'https://api.twitter.com/oauth/request_token',
                          params, settings, token, nc, ts)
        expected = 'OAuth oauth_callback="http%3A%2F%2Flocalhost%2Fsign-in-with-twitter%2F", oauth_consumer_key="cChZNFj6T5R0TigYB9yd1w", oauth_nonce="ea9ec8429b68d6b77cd5600adbbb0456", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1318467427", oauth_version="1.0", oauth_signature="F1Li3tvehgcraF8DMJ7OyxO4w9Y%3D"'
        self.assertEqual(res, expected)


