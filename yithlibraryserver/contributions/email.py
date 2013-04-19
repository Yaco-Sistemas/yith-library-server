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

from yithlibraryserver.email import send_email, send_email_to_admins


def send_thankyou_email(request, donation):
    return send_email(
        request,
        'yithlibraryserver.contributions:templates/email_thankyou',
        donation,
        'Thanks for your contribution!',
        [donation['email']],
    )


def send_notification_to_admins(request, donation):
    context = {
        'home_link': request.route_url('home'),
    }
    context.update(donation)
    return send_email_to_admins(
        request,
        'yithlibraryserver.contributions:templates/email_admin_notification',
        context,
        'A new donation was received!',
    )
