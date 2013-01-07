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

import colander
from deform.widget import TextAreaWidget

from yithlibraryserver.i18n import TranslationString as _


class ContactSchema(colander.MappingSchema):

    name = colander.SchemaNode(colander.String(), title=_('Name'))
    email = colander.SchemaNode(colander.String(), title=_('Email'))
    message = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(css_class='input-xxlarge', rows=10),
        title=_('Message'),
        )
