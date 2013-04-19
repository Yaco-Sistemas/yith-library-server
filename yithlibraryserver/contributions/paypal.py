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

import urlparse
import requests


class PayPalPayload(dict):

    def __init__(self, request, method):
        self['METHOD'] = method
        self['VERSION'] = '72.0'
        self['USER'] = request.registry.settings['paypal_user']
        self['PWD'] = request.registry.settings['paypal_password']
        self['SIGNATURE'] = request.registry.settings['paypal_signature']

    def add_payment_info(self, amount):
        self['PAYMENTREQUEST_0_AMT'] = amount
        self['PAYMENTREQUEST_0_ITEMAMT'] = amount
        self['PAYMENTREQUEST_0_DESC'] = 'Donation'
        self['PAYMENTREQUEST_0_CURRENCYCODE'] = 'USD'
        self['PAYMENTREQUEST_0_PAYMENTACTION'] = 'Sale'
        self['LOCALECODE'] = 'ES'

    def add_callbacks(self, return_url, cancel_url):
        self['RETURNURL'] = return_url
        self['CANCELURL'] = cancel_url

    def add_token(self, token, payerid):
        self['TOKEN'] = token
        self['PAYERID'] = payerid


class PayPalExpressCheckout(object):

    def __init__(self, request):
        self.request = request
        self.nvp_url = request.registry.settings['paypal_nvp_url']
        self.express_checkout_url = request.registry.settings['paypal_express_checkout_url']

    def get_express_checkout_token(self, amount):
        return_url = self.request.route_url('contributions_paypal_success_callback')
        cancel_url = self.request.route_url('contributions_paypal_cancel_callback')
        payload = PayPalPayload(self.request, 'SetExpressCheckout')
        payload.add_payment_info(amount)
        payload.add_callbacks(return_url, cancel_url)

        response = requests.post(self.nvp_url, data=payload)
        if response.ok:
            data = urlparse.parse_qs(response.text)
            ack = data['ACK'][0]
            if ack == 'Success':
                return data['TOKEN'][0]

    def get_express_checkout_url(self, token):
        url = self.express_checkout_url + '?cmd=_express-checkout&token=%s'
        return url % token

    def get_express_checkout_details(self, token, payerid):
        payload = PayPalPayload(self.request, 'GetExpressCheckoutDetails')
        payload.add_token(token, payerid)

        response = requests.post(self.nvp_url, data=payload)

        if response.ok:
            data = urlparse.parse_qs(response.text)
            ack = data['ACK'][0]
            if ack == 'Success':
                amount = data['AMT'][0]
                amount = int(amount.split('.')[0])
                return {
                    'amount': amount,
                    'firstname': data['FIRSTNAME'][0],
                    'lastname': data['LASTNAME'][0],
                    'city': data['SHIPTOCITY'][0],
                    'country': data['SHIPTOCOUNTRYNAME'][0],
                    'state': data['SHIPTOSTATE'][0],
                    'street': data['SHIPTOSTREET'][0],
                    'zip': data['SHIPTOZIP'][0],
                    'email': data['EMAIL'][0],
                }

    def do_express_checkout_payment(self, token, payerid, amount):
        payload = PayPalPayload(self.request, 'DoExpressCheckoutPayment')
        payload.add_payment_info(amount)
        payload.add_token(token, payerid)

        response = requests.post(self.nvp_url, data=payload)

        if response.ok:
            data = urlparse.parse_qs(response.text)
            ack = data['ACK'][0]
            if ack == 'Success':
                return True

        return False
