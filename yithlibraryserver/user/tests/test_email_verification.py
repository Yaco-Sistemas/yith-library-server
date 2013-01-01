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

from pyramid import testing
from pyramid.testing import DummyRequest

from pyramid_mailer import get_mailer

from yithlibraryserver.testing import TestCase
from yithlibraryserver.user.email_verification import EmailVerificationCode

class EmailVerificationCodeTests(TestCase):

    clean_collections = ('users', )

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        super(EmailVerificationCodeTests, self).setUp()

    def test_email_verification_code(self):
        evc = EmailVerificationCode()

        self.assertNotEqual(evc.code, None)

        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id})
        evc.store(self.db, user)

        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(user['email_verification_code'], evc.code)

        evc2 = EmailVerificationCode(evc.code)
        result = evc2.verify(self.db, 'john@example.com')
        self.assertTrue(result)

        evc2.remove(self.db, 'john@example.com', True)
        user = self.db.users.find_one({'_id': user_id})
        self.assertFalse('email_verification_code' in user)
        self.assertTrue(user['email_verified'])

        request = DummyRequest()
        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 0)
        evc2.send(request, user, 'http://example.com/verify')

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         'Please verify your email address')
        self.assertEqual(mailer.outbox[0].recipients,
                         ['john@example.com'])
