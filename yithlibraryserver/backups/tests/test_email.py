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
import unittest

import bson

from pyramid import testing
from pyramid.testing import DummyRequest

from pyramid_mailer import get_mailer

from yithlibraryserver.backups.email import get_day_to_send, send_passwords
from yithlibraryserver.backups.utils import get_backup_filename
from yithlibraryserver.testing import TestCase


class GetDayToSendTests(unittest.TestCase):

    def test_get_day_to_send(self):
        user = {}
        user['_id'] = bson.objectid.ObjectId('000000000000000000000001')
        self.assertEqual(5, get_day_to_send(user, 28))
        self.assertEqual(13, get_day_to_send(user, 30))
        self.assertEqual(6, get_day_to_send(user, 31))

        user['_id'] = bson.objectid.ObjectId('100000000000000000000000')
        self.assertEqual(5, get_day_to_send(user, 28))
        self.assertEqual(13, get_day_to_send(user, 30))
        self.assertEqual(6, get_day_to_send(user, 31))

        user['_id'] = bson.objectid.ObjectId('00000000000000000000000a')
        self.assertEqual(25, get_day_to_send(user, 28))
        self.assertEqual(1, get_day_to_send(user, 30))
        self.assertEqual(23, get_day_to_send(user, 31))

    def test_is_uniform_distribution(self):

        def fill_month(days, iterations):
            user = {}
            month = [0] * days
            for i in range(iterations):
                user['_id'] = bson.objectid.ObjectId()
                day = get_day_to_send(user, days)
                month[day] += 1
            return month

        month = fill_month(30, 1000)
        empty_days = [i for i, d in enumerate(month) if d == 0]
        self.assertEqual(empty_days, [])


class SendPasswordsTests(TestCase):

    clean_collections = ('users', 'passwords', )

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        super(SendPasswordsTests, self).setUp()

    def test_send_passwords(self):
        preferences_link = 'http://localhost/preferences'
        backups_link = 'http://localhost/backups'
        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id})

        request = DummyRequest()
        request.db = self.db
        mailer = get_mailer(request)

        self.assertFalse(send_passwords(request, user,
                                        preferences_link, backups_link))
        self.assertEqual(len(mailer.outbox), 0)

        # add some passwords
        self.db.passwords.insert({
                'owner': user_id,
                'password': 'secret1',
                })
        self.db.passwords.insert({
                'owner': user_id,
                'password': 'secret2',
                })

        request = DummyRequest()
        request.db = self.db
        mailer = get_mailer(request)

        self.assertTrue(send_passwords(request, user,
                                       preferences_link, backups_link))
        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.subject, "Your Yith Library's passwords")
        self.assertEqual(message.recipients, ['john@example.com'])
        self.assertTrue(preferences_link in message.body)
        self.assertTrue(backups_link in message.body)
        self.assertEqual(len(message.attachments), 1)
        attachment = message.attachments[0]
        self.assertEqual(attachment.content_type, 'application/yith')
        filename = get_backup_filename(datetime.date.today())
        self.assertEqual(attachment.filename, filename)
