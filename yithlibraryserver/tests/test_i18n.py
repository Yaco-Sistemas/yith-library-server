# Yith Library Server is a password storage server.
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

import unittest
from webtest import TestRequest

from pyramid import testing

from yithlibraryserver.i18n import deform_translator, locale_negotiator
from yithlibraryserver.testing import TestCase


class DeformTranslatorTests(unittest.TestCase):

    def setUp(self):
        request = testing.DummyRequest()
        testing.setUp(request=request)

    def tearDown(self):
        testing.tearDown()

    def test_deform_translator(self):
        self.assertEqual('foo', deform_translator('foo'))


class LocaleNegotiatorTests(TestCase):

    def test_locale_negotiator(self):
        request = TestRequest.blank('', {}, headers={})
        request.registry = self.testapp.app.registry
        self.assertEqual(locale_negotiator(request), 'en')

        request = TestRequest.blank('', {}, headers={
                'Accept-Language': 'es',
                })
        request.registry = self.testapp.app.registry
        self.assertEqual(locale_negotiator(request), 'es')

        request = TestRequest.blank('', {}, headers={
                'Accept-Language': 'de',  # german is not supported
                })
        request.registry = self.testapp.app.registry
        self.assertEqual(locale_negotiator(request), None)

        request = TestRequest.blank('', {}, headers={
                'Accept-Language': 'de, es',
                })
        request.registry = self.testapp.app.registry
        self.assertEqual(locale_negotiator(request), 'es')
