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

import hashlib

from yithlibraryserver.compat import url_encode


class Gravatar(object):

    def __init__(self, request, default_image_url):
        self.request = request
        self.default_image_url = default_image_url

    def get_email_hash(self, email):
        return hashlib.md5(email.lower().encode('utf-8')).hexdigest()

    def get_image_url(self, size=32):
        default_image_url = self.default_image_url

        email = self.get_email()
        if not email:
            return default_image_url

        email_hash = self.get_email_hash(email)
        parameters = {
            'd': default_image_url,
            's': size,
            }
        gravatar_url = 'https://www.gravatar.com/avatar/%s?%s' % (
            email_hash, url_encode(parameters))

        return gravatar_url

    def has_avatar(self):
        return self.get_email() is not None

    def get_email(self):
        user = self.request.user
        if user is None:
            return None

        email = user.get('email', '')
        if not email:
            return None

        return email


def get_gravatar(request):
    default_image_url = request.static_url(
        'yithlibraryserver:static/img/default_gravatar.png')
    return Gravatar(request, default_image_url)

