# Yith Library Server is a password storage server.
# Copyright (C) 2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

from mock import patch

from yithlibraryserver.testing import TestCase


class TestViews(TestCase):

    clean_collections = ('donations', )

    def test_contributions_index(self):
        res = self.testapp.get('/contribute')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('We need your help!', 'Spread the word',
                        'Translate', 'Write some code',
                        'Give us your money')

    def test_contributions_donate_bad_method(self):
        res = self.testapp.get('/contribute/donate', status=400)
        self.assertEqual(res.status, '400 Bad Request')

    def test_contributions_donate_bad_amount(self):
        res = self.testapp.post('/contribute/donate', {
                'amount': 'five',
                'submit': 'submit',
                }, status=400)
        self.assertEqual(res.status, '400 Bad Request')

    def test_contributions_donate(self):
        with patch('requests.post') as fake:
            fake.return_value.ok = True
            fake.return_value.text = 'ACK=Success&TOKEN=123'
            res = self.testapp.post('/contribute/donate', {
                    'amount': '5',
                    'submit': 'submit',
                    }, status=302)

            self.assertEqual(res.status, '302 Found')
            self.assertEqual(res.location, 'https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token=123')

            # USER, PWD, and SIGNATURE are Paypal testing values
            # They are set in yithlibrary.testing.TestCase.setUp
            fake.assert_called_with('https://api-3t.sandbox.paypal.com/nvp',
                                    data={
                    'METHOD': 'SetExpressCheckout',
                    'VERSION': '72.0',
                    'USER': 'sdk-three_api1.sdk.com',
                    'PWD': 'QFZCWN5HZM8VBG7Q',
                    'SIGNATURE': 'A-IzJhZZjhg29XQ2qnhapuwxIDzyAZQ92FRP5dqBzVesOkzbdUONzmOU',
                    'LOCALECODE': 'ES',
                    'PAYMENTREQUEST_0_ITEMAMT': 5,
                    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                    'PAYMENTREQUEST_0_CURRENCYCODE': 'USD',
                    'PAYMENTREQUEST_0_AMT': 5,
                    'PAYMENTREQUEST_0_DESC': 'Donation',
                    'RETURNURL': 'http://localhost/contribute/paypal-success-callback',
                    'CANCELURL': 'http://localhost/contribute/paypal-cancel-callback',
                    })
