# Yith Library Server is a password storage server.
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

import datetime
import bson

try:
    from pyramid.renderers import JSON
except ImportError:
    # backported from Pyramid 1.4
    import json
    from zope.interface import providedBy, Interface
    from zope.interface.registry import Components

    class IJSONAdapter(Interface):
        """
        Marker interface for objects that can convert an arbitrary object
        into a JSON-serializable primitive.
        """

    class JSON(object):

        def __init__(self, serializer=json.dumps, adapters=(), **kw):
            """ Any keyword arguments will be passed to the ``serializer``
            function."""
            self.serializer = serializer
            self.kw = kw
            self.components = Components()

        def add_adapter(self, type_or_iface, adapter):
            self.components.registerAdapter(adapter, (type_or_iface,),
                                            IJSONAdapter)

        def __call__(self, info):
            def _render(value, system):
                request = system.get('request')
                if request is not None:
                    response = request.response
                    ct = response.content_type
                    if ct == response.default_content_type:
                        response.content_type = 'application/json'
                default = self._make_default(request)
                return self.serializer(value, default=default, **self.kw)

            return _render

        def _make_default(self, request):
            def default(obj):
                obj_iface = providedBy(obj)
                adapters = self.components.adapters
                result = adapters.lookup((obj_iface,), IJSONAdapter,
                                         default=None)
                return result(obj, request)
            return default


json_renderer = JSON()


def bson_adapter(obj, request):
    return str(obj)
json_renderer.add_adapter(bson.ObjectId, bson_adapter)


def datetime_adapter(obj, request):
    return obj.isoformat()
json_renderer.add_adapter(datetime.datetime, datetime_adapter)
