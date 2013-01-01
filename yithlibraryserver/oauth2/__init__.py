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


def includeme(config):
    config.add_route('oauth2_developer_applications',
                     '/oauth2/applications')
    config.add_route('oauth2_developer_application_new',
                     '/oauth2/applications/new')
    config.add_route('oauth2_developer_application_edit',
                     '/oauth2/applications/{app}/edit')
    config.add_route('oauth2_developer_application_delete',
                     '/oauth2/applications/{app}/delete')

    config.add_route('oauth2_authorization_endpoint',
                     '/oauth2/endpoints/authorization')
    config.add_route('oauth2_token_endpoint',
                     '/oauth2/endpoints/token')

    config.add_route('oauth2_authorized_applications',
                     '/oauth2/authorized-applications')
    config.add_route('oauth2_revoke_application',
                     '/oauth2/applications/{app}/revoke')

    config.add_route('oauth2_clients', '/oauth2/clients')
