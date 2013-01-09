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

import logging

from yithlibraryserver.i18n import TranslationString as _

log = logging.getLogger(__name__)


class IdentityProvider(object):

    def __init__(self, name):
        self.name = name

    @property
    def route_path(self):
        return '%s_login' % self.name

    @property
    def image_path(self):
        return 'yithlibraryserver:static/img/%s-logo.png' % self.name

    @property
    def message(self):
        return _('Log in with ${idp}', mapping={'idp': self.name.capitalize()})


def add_identity_provider(config, name):
    log.debug('Registering identity provider "%s"' % name)

    if not hasattr(config.registry, 'identity_providers'):
        config.registry.identity_providers = []

    config.registry.identity_providers.append(IdentityProvider(name))
