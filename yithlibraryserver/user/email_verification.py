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

import uuid

from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


class EmailVerificationCode(object):

    def __init__(self, code=None):
        if code is None:
            self.code = self._generate_code()
        else:
            self.code = code

    def _generate_code(self):
        return str(uuid.uuid4())

    def store(self, db, user):
        result = db.users.update({'_id': user['_id']}, {
                '$set': {'email_verification_code': self.code},
                }, safe=True)
        return result['n'] == 1

    def remove(self, db, email, verified):
        result = db.users.update({
                'email_verification_code': self.code,
                'email': email,
                }, {
                '$unset': {'email_verification_code': 1},
                '$set': {'email_verified': verified},
                }, safe=True)
        return result['n'] == 1

    def verify(self, db, email):
        result = db.users.find_one({
                'email': email,
                'email_verification_code': self.code,
                })
        return result is not None

    def send(self, request, user, url):
        link = '%s?code=%s&email=%s' % (url, self.code, user['email'])
        text_body = render(
            'yithlibraryserver.user:templates/email_verification_code.txt',
            {'link': link, 'user': user},
            request=request,
            )
        # chamaleon txt templates are rendered as utf-8 bytestrings
        text_body = text_body.decode('utf-8')

        html_body = render(
            'yithlibraryserver.user:templates/email_verification_code.pt',
            {'link': link, 'user': user},
            request=request,
            )
        message = Message(subject='Please verify your email address',
                          recipients=[user['email']],
                          body=text_body,
                          html=html_body)

        get_mailer(request).send(message)
