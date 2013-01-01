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

import binascii
import hashlib
import hmac
import random
import time

from yithlibraryserver.compat import url_quote


def quote(value):
    return url_quote(value, safe='')


def nonce(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def timestamp():
    return int(time.time())


def sign(method, url, original_params, consumer_secret, oauth_token):
    # 1. create the parameter string
    param_string = '&'.join(['%s=%s' % (key, value)
                             for key, value in sorted(original_params)])

    # 2. create signature base string
    signature_base = '%s&%s&%s' % (
        method.upper(), quote(url), quote(param_string),
        )

    # 3. create the signature key
    key = '%s&%s' % (quote(consumer_secret), quote(oauth_token))

    # 4. calculate the signature
    hashed = hmac.new(key.encode('ascii'),
                      signature_base.encode('ascii'),
                      hashlib.sha1)
    return quote(binascii.b2a_base64(hashed.digest())[:-1])


def auth_header(method, url, original_params, settings, oauth_token='',
                nonce_=None, timestamp_=None):
    params = list(original_params) + [
        ('oauth_consumer_key', settings['twitter_consumer_key']),
        ('oauth_nonce', nonce_ or nonce()),
        ('oauth_signature_method', 'HMAC-SHA1'),
        ('oauth_timestamp', str(timestamp_ or timestamp())),
        ('oauth_version', '1.0'),
        ]
    params = [(quote(key), quote(value)) for key, value in params]

    signature = sign(method, url, params,
                     settings['twitter_consumer_secret'], oauth_token)
    params.append(('oauth_signature', signature))

    header = ", ".join(['%s="%s"' % (key, value) for key, value in params])

    return 'OAuth %s' % header
