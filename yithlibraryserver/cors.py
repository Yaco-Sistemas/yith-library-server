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

import logging

log = logging.getLogger(__name__)


class CORSManager(object):

    def __init__(self, allowed_origins):
        self.allowed_origins = allowed_origins.split(' ')

    def add_cors_header(self, request, response):
        if 'Origin' in request.headers:
            origin = request.headers['Origin']
            if origin in self.allowed_origins:
                log.debug('Origin %s is allowed: %s' %
                          (origin, ' '.join(self.allowed_origins)))
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                log.debug('Origin %s is not allowed: %s' %
                          (origin, ' '.join(self.allowed_origins)))
