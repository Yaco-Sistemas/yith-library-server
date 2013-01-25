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

from pyramid.paster import bootstrap

from yithlibraryserver.compat import PY3


def safe_print(value):
    if PY3:  # pragma: no cover
        print(value)
    else:  # pragma: no cover
        print(value.encode('utf-8'))


def setup_simple_command(name, description):
    usage = name + ": %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        safe_print('You must provide at least one argument')
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    return settings, closer, env, args[1:]


def get_user_display_name(user):
    return '%s %s <%s>' % (user.get('first_name', ''),
                           user.get('last_name', ''),
                           user.get('email', ''))
