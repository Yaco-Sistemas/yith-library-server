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

import datetime

from pyramid import testing

from pyramid_mailer import get_mailer

from yithlibraryserver.testing import TestCase
from yithlibraryserver.contributions.email import send_thankyou_email
from yithlibraryserver.contributions.email import send_notification_to_admins


class SendEmailTests(TestCase):

    def setUp(self):
        self.admin_emails = ['admin1@example.com', 'admin2@example.com']
        self.config = testing.setUp(settings={
                'admin_emails': self.admin_emails,
                })
        self.config.include('pyramid_mailer.testing')
        self.config.include('yithlibraryserver')
        super(SendEmailTests, self).setUp()

    def test_send_thankyou_email(self):
        request = testing.DummyRequest()
        mailer = get_mailer(request)

        self.assertEqual(len(mailer.outbox), 0)

        donation = {
            'amount': 10,
            'firstname': 'John',
            'lastname': 'Doe',
            'city': 'Springfield',
            'country': 'Exampleland',
            'state': 'Example',
            'street': 'Main Street 10',
            'zip': '12345678',
            'email': 'john@example.com',
            'creation': datetime.datetime.utcnow(),
            'send_sticker': True,
        }
        send_thankyou_email(request, donation)

        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.subject, 'Thanks for your contribution!')
        self.assertEqual(message.recipients, ['john@example.com'])

    def test_send_notification_to_admins(self):
        request = testing.DummyRequest()
        mailer = get_mailer(request)

        self.assertEqual(len(mailer.outbox), 0)

        donation = {
            'amount': 10,
            'firstname': 'John',
            'lastname': 'Doe',
            'city': 'Springfield',
            'country': 'Exampleland',
            'state': 'Example',
            'street': 'Main Street 10',
            'zip': '12345678',
            'email': 'john@example.com',
            'creation': datetime.datetime.utcnow(),
            'send_sticker': True,
            'user': None,
        }
        send_notification_to_admins(request, donation)

        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.subject, 'A new donation was received!')
        self.assertEqual(message.recipients, self.admin_emails)
