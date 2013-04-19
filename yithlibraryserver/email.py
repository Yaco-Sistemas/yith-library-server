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
from pyramid_mailer.message import Message


def create_message(request, template, context, subject, recipients,
                   attachments=None, extra_headers=None):
    text_body = render(template + '.txt', context, request=request)
    # chamaleon txt templates are rendered as utf-8 bytestrings
    text_body = text_body.decode('utf-8')

    html_body = render(template + '.pt', context, request=request)

    extra_headers = extra_headers or {}

    message = Message(
        subject=subject,
        recipients=recipients,
        body=text_body,
        html=html_body,
        extra_headers=extra_headers,
    )

    if attachments is not None:
        for attachment in attachments:
            message.attach(attachment)

    return message


def send_email(request, template, context, subject, recipients,
               attachments=None, extra_headers=None):
    message = create_message(request, template, context, subject, recipients,
                             attachments, extra_headers)
    return get_mailer(request).send(message)


def send_email_to_admins(request, template, context, subject,
                         attachments=None, extra_headers=None):
    admin_emails = request.registry.settings['admin_emails']
    if admin_emails:
        return send_email(request, template, context, subject, admin_emails,
                          attachments, extra_headers)
