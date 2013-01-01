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

from yithlibraryserver import read_setting_from_env


def includeme(config):
    settings = config.registry.settings

    for key, default in (
        ('audience', None),
        ('verifier_url', 'https://verifier.login.persona.org/verify'),
        ):

        option = 'persona_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    if settings['persona_audience']:
        config.add_route('persona_login', '/persona/login')
        config.add_view('.views.persona_login',
                        route_name='persona_login', renderer='string')

        config.add_identity_provider('persona')
