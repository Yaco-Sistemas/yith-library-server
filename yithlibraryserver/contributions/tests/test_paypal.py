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

from pyramid import testing

from yithlibraryserver.contributions.paypal import PayPalPayload


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
