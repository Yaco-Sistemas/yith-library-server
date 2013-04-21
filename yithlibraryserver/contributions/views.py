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

import random

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.i18n import get_locale_name
from pyramid.view import view_config

from yithlibraryserver.contributions.email import send_thankyou_email
from yithlibraryserver.contributions.email import send_notification_to_admins
from yithlibraryserver.contributions.models import create_donation
from yithlibraryserver.contributions.models import include_sticker
from yithlibraryserver.contributions.paypal import PayPalExpressCheckout
from yithlibraryserver.i18n import TranslationString as _


@view_config(route_name='contributions_index',
             renderer='templates/contributions_index.pt')
def contributions_index(request):
    locale_name = get_locale_name(request)
    return {'locale': locale_name, 'random': random}


@view_config(route_name='contributions_donate',
             renderer='string')
def contributions_donate(request):
    if 'submit' in request.POST:
        paypal = PayPalExpressCheckout(request)
        amount = request.POST.get('amount', '1')
        try:
            amount = int(amount)
        except ValueError:
            return HTTPBadRequest('Amount must be an integer')
        token = paypal.get_express_checkout_token(amount)
        return HTTPFound(paypal.get_express_checkout_url(token))

    return HTTPBadRequest('Wrong action or method')


@view_config(route_name='contributions_paypal_success_callback',
             renderer='templates/contributions_confirm.pt')
def contributions_paypal_success(request):
    error_msg = _('There was a problem in the confirmation process. Please start the checkout again')
    if request.method == 'POST':
        if 'submit' in request.POST:
            token = request.POST.get('token', None)
            payerid = request.POST.get('payerid', None)
            amount = request.POST.get('amount', None)

            success = False

            if token and payerid and amount:
                try:
                    amount = int(amount)
                except ValueError:
                    return HTTPBadRequest('Amount must be an integer')

                paypal = PayPalExpressCheckout(request)
                success = paypal.do_express_checkout_payment(token, payerid,
                                                             amount)

            if success:
                donation = create_donation(request, request.POST)
                send_thankyou_email(request, donation)
                send_notification_to_admins(request, donation)
                request.session.flash(
                    _('Thank you very much for your great contribution'),
                    'success',
                )
            else:
                request.session.flash(error_msg, 'error')

            return HTTPFound(location=request.route_path('contributions_index'))

        elif 'cancel' in request.POST:
            return HTTPFound(location=request.route_path('contributions_paypal_cancel_callback'))

        else:
            return HTTPBadRequest('Wrong action')

    else:
        token = request.GET.get('token', None)
        payerid = request.GET.get('PayerID', None)

        if token and payerid:
            paypal = PayPalExpressCheckout(request)
            details = paypal.get_express_checkout_details(token, payerid)
            details.update({'token': token, 'payerid': payerid})
            details['include_sticker'] = include_sticker(details['amount'])
            return details
        else:
            request.session.flash(error_msg, 'error')
            return HTTPFound(location=request.route_path('contributions_index'))


@view_config(route_name='contributions_paypal_cancel_callback',
             renderer='string')
def contributions_paypal_cancel(request):
    request.session.flash(
        _('Thanks for considering donating to Yith Library. We will be ready if you change your mind'),
        'info',
    )
    return HTTPFound(location=request.route_path('contributions_index'))
