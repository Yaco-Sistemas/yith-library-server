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

from yithlibraryserver.compat import text_type


class User(dict):

    def __unicode__(self):
        result = self.get('screen_name', '')
        if result:
            return result

        result = ' '.join([self.get('first_name', ''),
                           self.get('last_name', '')])
        result = result.strip()
        if result:
            return result

        result = self.get('email', '')
        if result:
            return result

        return text_type(self['_id'])

    # py3 compatibility
    def __str__(self):
        return self.__unicode__()
