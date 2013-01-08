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

import colander
from deform.widget import TextAreaWidget, TextInputWidget

from yithlibraryserver.i18n import TranslationString as _


class ApplicationSchema(colander.MappingSchema):

    name = colander.SchemaNode(colander.String(), title=_('Name'))
    main_url = colander.SchemaNode(
        colander.String(),
        title=_('Main URL'),
        widget=TextInputWidget(css_class='input-xlarge'),
        )
    callback_url = colander.SchemaNode(
        colander.String(),
        title=_('Callback URL'),
        widget=TextInputWidget(css_class='input-xlarge'),
        )
    production_ready = colander.SchemaNode(
        colander.Boolean(),
        title=_('Production ready'),
        missing=False,
        )
    image_url = colander.SchemaNode(
        colander.String(),
        title=_('Image URL'),
        missing='',
        widget=TextInputWidget(css_class='input-xlarge'),
        )
    description = colander.SchemaNode(
        colander.String(),
        title=_('Description'),
        missing='',
        widget=TextAreaWidget(css_class='input-xlarge'),
        )


class ReadOnlyTextInputWidget(TextInputWidget):

    def serialize(self, field, cstruct, readonly=False):
        return super(ReadOnlyTextInputWidget, self).serialize(field,
                                                              cstruct=cstruct,
                                                              readonly=True)


class FullApplicationSchema(ApplicationSchema):

    client_id = colander.SchemaNode(
        colander.String(),
        title=_('Client Id'),
        widget=ReadOnlyTextInputWidget(css_class='input-xlarge'),
        )
    client_secret = colander.SchemaNode(
        colander.String(),
        title=_('Client secret'),
        widget=ReadOnlyTextInputWidget(css_class='input-xlarge'),
        )
