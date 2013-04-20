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

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Attachment

from yithlibraryserver.email import create_message, send_email
from yithlibraryserver.email import send_email_to_admins
from yithlibraryserver.testing import TestCase


class CreateMessageTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def test_create_message(self):
        request = testing.DummyRequest()
        message = create_message(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message', ['john@example.com'],
        )
        self.assertEquals(message.subject, 'Testing message')
        self.assertEquals(message.html, '<p>Hello John,</p>\n\n<p>this is your email address: john@example.com</p>')
        self.assertEquals(message.body, 'Hello John,\n\nthis is your email address: john@example.com\n')
        self.assertEquals(message.recipients, ['john@example.com'])
        self.assertEquals(message.attachments, [])
        self.assertEquals(message.extra_headers, {})

    def test_create_message_with_attachments(self):
        request = testing.DummyRequest()

        attachment = Attachment('foo.txt', 'text/plain', 'test')

        message = create_message(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message', ['john@example.com'],
            attachments=[attachment],
        )
        self.assertEquals(message.subject, 'Testing message')
        self.assertEquals(message.html, '<p>Hello John,</p>\n\n<p>this is your email address: john@example.com</p>')
        self.assertEquals(message.body, 'Hello John,\n\nthis is your email address: john@example.com\n')
        self.assertEquals(message.recipients, ['john@example.com'])
        self.assertEquals(message.extra_headers, {})
        self.assertEquals(len(message.attachments), 1)
        a = message.attachments[0]
        self.assertEquals(a.filename, 'foo.txt')
        self.assertEquals(a.content_type, 'text/plain')
        self.assertEquals(a.data, 'test')

    def test_create_message_with_extra_headers(self):
        request = testing.DummyRequest()

        message = create_message(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message', ['john@example.com'],
            extra_headers={'foo': 'bar'},
        )
        self.assertEquals(message.subject, 'Testing message')
        self.assertEquals(message.html, '<p>Hello John,</p>\n\n<p>this is your email address: john@example.com</p>')
        self.assertEquals(message.body, 'Hello John,\n\nthis is your email address: john@example.com\n')
        self.assertEquals(message.recipients, ['john@example.com'])
        self.assertEquals(message.attachments, [])
        self.assertEquals(message.extra_headers, {'foo': 'bar'})


class SendEmailTests(TestCase):

    def setUp(self):
        self.admin_emails = ['admin1@example.com', 'admin2@example.com']
        self.config = testing.setUp(settings={
                'admin_emails': self.admin_emails,
                })
        self.config.include('pyramid_mailer.testing')
        self.config.include('yithlibraryserver')
        super(SendEmailTests, self).setUp()

    def test_send_email(self):
        request = testing.DummyRequest()
        mailer = get_mailer(request)

        send_email(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message', ['john@example.com'],
        )

        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEquals(message.subject, 'Testing message')
        self.assertEquals(message.html, '<p>Hello John,</p>\n\n<p>this is your email address: john@example.com</p>')
        self.assertEquals(message.body, 'Hello John,\n\nthis is your email address: john@example.com\n')
        self.assertEquals(message.recipients, ['john@example.com'])
        self.assertEquals(message.attachments, [])
        self.assertEquals(message.extra_headers, {})

    def test_send_email_to_admins(self):
        request = testing.DummyRequest()
        mailer = get_mailer(request)

        send_email_to_admins(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message',
        )

        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEquals(message.subject, 'Testing message')
        self.assertEquals(message.html, '<p>Hello John,</p>\n\n<p>this is your email address: john@example.com</p>')
        self.assertEquals(message.body, 'Hello John,\n\nthis is your email address: john@example.com\n')
        self.assertEquals(message.recipients, self.admin_emails)
        self.assertEquals(message.attachments, [])
        self.assertEquals(message.extra_headers, {})


class SendEmailNoAdminsTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={
                'admin_emails': [],
                })
        self.config.include('pyramid_mailer.testing')
        self.config.include('yithlibraryserver')
        super(SendEmailNoAdminsTests, self).setUp()

    def test_send_email_to_admins(self):
        request = testing.DummyRequest()
        mailer = get_mailer(request)

        send_email_to_admins(
            request,
            'yithlibraryserver.tests:templates/email_test',
            {'name': 'John', 'email': 'john@example.com'},
            'Testing message',
        )

        # no email is actually send since there is no admin
        # emails configured
        self.assertEqual(len(mailer.outbox), 0)
