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

import sys
import types

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    long = int
else:  # pragma: no cover
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    long = long

if PY3:  # pragma: no cover
    from urllib import parse
    urlparse = parse
    from urllib.parse import quote as url_quote
    from urllib.parse import urlencode as url_encode
else:  # pragma: no cover
    import urlparse
    from urllib import quote as url_quote
    from urllib import urlencode as url_encode

if PY3:  # pragma: no cover
    from base64 import decodebytes, encodebytes
else:  # pragma: no cover
    from base64 import decodestring as decodebytes
    from base64 import encodestring as encodebytes

if PY3:  # pragma: no cover
    def encode_header(obj):  # pragma: no cover
        return obj
else:  # pragma: no cover
    def encode_header(obj):  # pragma: no cover
        return obj.encode('utf-8')

if PY3:  # pragma: no cover
    from io import StringIO
else:  # pragma: no cover
    from StringIO import StringIO
