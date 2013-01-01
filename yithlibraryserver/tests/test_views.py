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

from pyramid_mailer import get_mailer

from yithlibraryserver import testing


class ViewTests(testing.TestCase):

    def test_home(self):
        res = self.testapp.get('/')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Start using it today', no='Get your passwords')

        # Log in
        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                }, safe=True)
        self.set_user_cookie(str(user_id))
        res = self.testapp.get('/')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Get your passwords', no='Start using it today')

    def test_contact(self):
        res = self.testapp.get('/contact')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('Name')
        res.mustcontain('Email')
        res.mustcontain('Message')

        # The three fields are required
        res = self.testapp.post('/contact', {
                'submit': 'Send message',
                })
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('class="error" id="error-deformField1">Required')
        res.mustcontain('class="error" id="error-deformField2">Required')
        res.mustcontain('class="error" id="error-deformField3">Required')

        res = self.testapp.post('/contact', {
                'name': 'John',
                'email': 'john@example.com',
                'message': 'Testing message',
                'submit': 'Send message',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')
        # check that the email was sent
        res.request.registry = self.testapp.app.registry
        mailer = get_mailer(res.request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         "John sent a message from Yith's contact form")
        self.assertEqual(mailer.outbox[0].recipients,
                         ['admin1@example.com', 'admin2@example.com'])
        self.assertEqual(mailer.outbox[0].extra_headers,
                         {'Reply-To': 'john@example.com'})

        # if the user is authenticated, prefill the name and
        # email fields
        # Log in
        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'email_verified': True,
                }, safe=True)
        self.set_user_cookie(str(user_id))

        res = self.testapp.get('/contact')
        self.assertEqual(res.status, '200 OK')
        res.mustcontain('John')
        res.mustcontain('john@example.com')

        # simulate a cancel
        res = self.testapp.post('/contact', {
                'cancel': 'Cancel',
                }, status=302)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')

        # remove the admin emails configuration
        self.testapp.app.registry.settings['admin_emails'] = []

        res = self.testapp.post('/contact', {
                'name': 'John',
                'email': 'john@example.com',
                'message': 'Testing message',
                'submit': 'Send message',
                })
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/')
        # check that the email was *not* sent
        res.request.registry = self.testapp.app.registry
        mailer = get_mailer(res.request)
        self.assertEqual(len(mailer.outbox), 1)

    def test_tos(self):
        res = self.testapp.get('/tos')
        self.assertEqual(res.status, '200 OK')
