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

import optparse
import textwrap
import sys

import transaction

from pyramid.paster import bootstrap
from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from yithlibraryserver.compat import urlparse
from yithlibraryserver.scripts.reports import get_passwords_map
from yithlibraryserver.scripts.utils import safe_print
from yithlibraryserver.scripts.utils import get_user_display_name


def get_all_users_with_passwords_and_email(db):
    all_passwords = list(db.passwords.find())
    passwords_map = get_passwords_map(all_passwords)
    for user in db.users.find():
        if not user['email']:
            continue

        if not user['_id'] in passwords_map:
            continue

        yield user


def send_email(request, email_template, user, preferences_link):
    safe_print('Sending email to %s' % get_user_display_name(user))

    text_body = render(
        'yithlibraryserver.scripts:templates/%s.txt' % email_template,
        {'user': user, 'preferences_link': preferences_link},
        request=request,
        )
    # chamaleon txt templates are rendered as utf-8 bytestrings
    text_body = text_body.decode('utf-8')

    html_body = render(
        'yithlibraryserver.scripts:templates/%s.pt' % email_template,
        {'user': user, 'preferences_link': preferences_link},
        request=request,
        )

    message = Message(subject="Yith Library announcement",
                      recipients=[user['email']],
                      body=text_body,
                      html=html_body)
    return message


def announce():
    usage = "migrate: %prog config_uri migration_name"
    description = "Add a 'send_email_periodically' preference to every user."
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if len(args) != 2:
        safe_print('You must provide two arguments. '
                   'The first one is the config file and the '
                   'second one is the email template.')
        return 2
    config_uri = args[0]
    email_template = args[1]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    try:

        db = settings['mongodb'].get_database()
        request = env['request']

        public_url_root = settings['public_url_root']
        preferences_link = urlparse.urljoin(
            public_url_root,
            request.route_path('user_preferences'))

        tx = transaction.begin()

        mailer = get_mailer(request)

        for user in get_all_users_with_passwords_and_email(db):
            message = send_email(request, email_template, user,
                                 preferences_link)
            mailer.send(message)

        tx.commit()

    finally:
        closer()


if __name__ == '__main__':  # pragma: no cover
    announce()
