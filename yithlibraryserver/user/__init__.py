# Yith Library Server is a password storage server.
# Copyright (C) 2012 Yaco Sistemas
# Copyright (C) 2012 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

from yithlibraryserver.user.idp import add_identity_provider
from yithlibraryserver.user.security import get_user


def includeme(config):
    config.add_directive('add_identity_provider', add_identity_provider)

    config.set_request_property(get_user, 'user', reify=True)

    config.add_route('login', '/login')
    config.add_route('register_new_user', '/register')
    config.add_route('logout', '/logout')
    config.add_route('user_destroy', '/destroy')
    config.add_route('user_profile', '/profile')
    config.add_route('user_send_email_verification_code',
                     '/send-email-verification-code')
    config.add_route('user_verify_email', '/verify-email')
    config.add_route('user_merge_accounts', '/merge-accounts')
