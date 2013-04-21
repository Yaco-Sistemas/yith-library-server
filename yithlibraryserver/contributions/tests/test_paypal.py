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

import unittest

from mock import patch

from pyramid import testing

from yithlibraryserver.contributions.paypal import PayPalPayload
from yithlibraryserver.contributions.paypal import PayPalExpressCheckout


class PayPalPayloadTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={
                'paypal_user': 'paypal_user',
                'paypal_password': 'paypal_password',
                'paypal_signature': 'paypal_signature',
                })

    def tearDown(self):
        testing.tearDown()

    def test_basic_payload(self):
        request = testing.DummyRequest()

        payload = PayPalPayload(request, 'method1')
        self.assertEqual(payload, {
                'METHOD': 'method1',
                'VERSION': '72.0',
                'USER': 'paypal_user',
                'PWD': 'paypal_password',
                'SIGNATURE': 'paypal_signature',
                })

    def test_payment_info(self):
        request = testing.DummyRequest()

        payload = PayPalPayload(request, 'method_with_info')
        payload.add_payment_info(10)
        self.assertEqual(payload, {
                'METHOD': 'method_with_info',
                'VERSION': '72.0',
                'USER': 'paypal_user',
                'PWD': 'paypal_password',
                'SIGNATURE': 'paypal_signature',
                'PAYMENTREQUEST_0_AMT': 10,
                'PAYMENTREQUEST_0_ITEMAMT': 10,
                'PAYMENTREQUEST_0_DESC': 'Donation',
                'PAYMENTREQUEST_0_CURRENCYCODE': 'USD',
                'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                'LOCALECODE': 'ES',
                })

    def test_callbacks(self):
        request = testing.DummyRequest()

        payload = PayPalPayload(request, 'method_with_callbacks')
        payload.add_callbacks('http://example.com/success',
                              'http://example.com/cancel')
        self.assertEqual(payload, {
                'METHOD': 'method_with_callbacks',
                'VERSION': '72.0',
                'USER': 'paypal_user',
                'PWD': 'paypal_password',
                'SIGNATURE': 'paypal_signature',
                'RETURNURL': 'http://example.com/success',
                'CANCELURL': 'http://example.com/cancel',
                })

    def test_token(self):
        request = testing.DummyRequest()

        payload = PayPalPayload(request, 'method_with_callbacks')
        payload.add_token('12345', '6789')
        self.assertEqual(payload, {
                'METHOD': 'method_with_callbacks',
                'VERSION': '72.0',
                'USER': 'paypal_user',
                'PWD': 'paypal_password',
                'SIGNATURE': 'paypal_signature',
                'TOKEN': '12345',
                'PAYERID': '6789',
                })


class PayPalExpressCheckoutTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={
                'paypal_user': 'paypal_user',
                'paypal_password': 'paypal_password',
                'paypal_signature': 'paypal_signature',
                'paypal_nvp_url': 'http://paypal.com/nvp',
                'paypal_express_checkout_url': 'http://paypal.com/express_checkout',
                })
        self.config.include('yithlibraryserver')
        self.config.include('yithlibraryserver.contributions')

    def test_express_checkout_token(self):
        request = testing.DummyRequest()
        pec = PayPalExpressCheckout(request)
        self.assertEqual(pec.nvp_url, 'http://paypal.com/nvp')
        self.assertEqual(pec.express_checkout_url,
                         'http://paypal.com/express_checkout')

        with patch('requests.post') as fake:
            fake.return_value.ok = True
            fake.return_value.text = 'ACK=Success&TOKEN=123'
            result = pec.get_express_checkout_token(5)
            fake.assert_called_with('http://paypal.com/nvp', data={
                    'METHOD': 'SetExpressCheckout',
                    'VERSION': '72.0',
                    'USER': 'paypal_user',
                    'PWD': 'paypal_password',
                    'SIGNATURE': 'paypal_signature',
                    'LOCALECODE': 'ES',
                    'PAYMENTREQUEST_0_ITEMAMT': 5,
                    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                    'PAYMENTREQUEST_0_CURRENCYCODE': 'USD',
                    'PAYMENTREQUEST_0_AMT': 5,
                    'PAYMENTREQUEST_0_DESC': 'Donation',
                    'RETURNURL': 'http://example.com/contribute/paypal-success-callback',
                    'CANCELURL': 'http://example.com/contribute/paypal-cancel-callback',
                    })
            self.assertEqual(result, '123')

        self.assertEqual(
            pec.get_express_checkout_url('123'),
            'http://paypal.com/express_checkout?cmd=_express-checkout&token=123')

    def test_express_checkout_details(self):
        request = testing.DummyRequest()
        pec = PayPalExpressCheckout(request)
        self.assertEqual(pec.nvp_url, 'http://paypal.com/nvp')
        self.assertEqual(pec.express_checkout_url,
                         'http://paypal.com/express_checkout')

        with patch('requests.post') as fake:
            fake.return_value.ok = True
            fake.return_value.text = 'ACK=Success&AMT=5.00&FIRSTNAME=John&LASTNAME=Doe&SHIPTOCITY=ExampleCity&SHIPTOCOUNTRYNAME=ExampleCountry&SHIPTOSTATE=ExampleState&SHIPTOSTREET=ExampleStreet&SHIPTOZIP=123456&EMAIL=john@example.com'
            result = pec.get_express_checkout_details('123', '456')
            fake.assert_called_with('http://paypal.com/nvp', data={
                    'METHOD': 'GetExpressCheckoutDetails',
                    'VERSION': '72.0',
                    'USER': 'paypal_user',
                    'PWD': 'paypal_password',
                    'SIGNATURE': 'paypal_signature',
                    'TOKEN': '123',
                    'PAYERID': '456',
                    })
            self.assertEqual(result, {
                    'amount': 5,
                    'firstname': 'John',
                    'lastname': 'Doe',
                    'city': 'ExampleCity',
                    'country': 'ExampleCountry',
                    'state': 'ExampleState',
                    'street': 'ExampleStreet',
                    'zip': '123456',
                    'email': 'john@example.com',
                    })

    def test_express_checkout_payment(self):
        request = testing.DummyRequest()
        pec = PayPalExpressCheckout(request)
        self.assertEqual(pec.nvp_url, 'http://paypal.com/nvp')
        self.assertEqual(pec.express_checkout_url,
                         'http://paypal.com/express_checkout')

        with patch('requests.post') as fake:
            fake.return_value.ok = True
            fake.return_value.text = 'ACK=Success'
            result = pec.do_express_checkout_payment('123', '456', 5)
            fake.assert_called_with('http://paypal.com/nvp', data={
                    'METHOD': 'DoExpressCheckoutPayment',
                    'VERSION': '72.0',
                    'USER': 'paypal_user',
                    'PWD': 'paypal_password',
                    'SIGNATURE': 'paypal_signature',
                    'TOKEN': '123',
                    'PAYERID': '456',
                    'LOCALECODE': 'ES',
                    'PAYMENTREQUEST_0_ITEMAMT': 5,
                    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                    'PAYMENTREQUEST_0_CURRENCYCODE': 'USD',
                    'PAYMENTREQUEST_0_AMT': 5,
                    'PAYMENTREQUEST_0_DESC': 'Donation',
                    })
            self.assertTrue(result)

            # Simulate a failure
            fake.return_value.ok = True
            fake.return_value.text = 'ACK=Failure'
            result = pec.do_express_checkout_payment('123', '456', 5)
            self.assertFalse(result)
