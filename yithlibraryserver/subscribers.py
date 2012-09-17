# Yith Library Server is a password storage server.
# Copyright (C) 2012 Yaco Sistemas
# Copyright (C) 2012 Alejandro Blanco Escudero <korosu.itai@gmail.com>
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

from pyramid.events import BeforeRender, NewRequest
from pyramid.renderers import get_renderer

from yithlibraryserver.db import get_db
from yithlibraryserver.user.security import get_user


def add_cors_headers_response(event):
    cors_manager = event.request.registry.settings['cors_manager']

    def cors_headers_callback(request, response):
        return cors_manager.add_cors_header(request, response)

    event.request.add_response_callback(cors_headers_callback)


def add_base_template(event):
    base_renderer = get_renderer('yithlibraryserver:templates/base.pt')
    event.update({'base': base_renderer.implementation()})


def includeme(config):
    config.set_request_property(get_db, 'db', reify=True)
    config.set_request_property(get_user, 'user', reify=True)

    config.add_subscriber(add_cors_headers_response, NewRequest)
    config.add_subscriber(add_base_template, BeforeRender)
