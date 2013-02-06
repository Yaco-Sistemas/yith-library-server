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

from pyramid.renderers import render
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Attachment, Message

from yithlibraryserver.backups.utils import get_backup_filename
from yithlibraryserver.backups.utils import get_user_passwords, compress


def get_day_to_send(user, days_of_month):
    """Sum the ordinal of each character in user._id % days_of_month"""
    return sum([ord(chr) for chr in str(user['_id'])]) % days_of_month


def send_passwords(request, user, preferences_link, backups_link):
    passwords = get_user_passwords(request.db, user)
    if not passwords:
        return False

    text_body = render(
        'yithlibraryserver.backups:templates/email_passwords.txt',
        {'user': user,
         'preferences_link': preferences_link,
         'backups_link': backups_link},
        request=request,
        )
    # chamaleon txt templates are rendered as utf-8 bytestrings
    text_body = text_body.decode('utf-8')

    html_body = render(
        'yithlibraryserver.backups:templates/email_passwords.pt',
        {'user': user,
         'preferences_link': preferences_link,
         'backups_link': backups_link},
        request=request,
        )

    message = Message(subject="Your Yith Library's passwords",
                      recipients=[user['email']],
                      body=text_body,
                      html=html_body)

    today = request.datetime_service.date_today()
    attachment = Attachment(get_backup_filename(today),
                            "application/yith",
                            compress(passwords))

    message.attach(attachment)

    mailer = get_mailer(request)
    mailer.send(message)
    return True
