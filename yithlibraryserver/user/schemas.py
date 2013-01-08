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


class EmailWidget(TextInputWidget):

    email_verified_template = 'email_verified'

    def serialize(self, field, cstruct, readonly=False):
        email_output = super(EmailWidget, self).serialize(
            field,
            cstruct.get('email', ''),
            readonly,
            )

        pstruct = field.schema.deserialize(cstruct)
        email_verified_output = field.renderer(
            self.email_verified_template,
            email=pstruct.get('email', ''),
            email_verified=pstruct.get('email_verified', False),
            )

        return email_output + email_verified_output

    def deserialize(self, field, pstruct):
        return {
            'email': super(EmailWidget, self).deserialize(field, pstruct),
            # The email_verified attr is readonly and
            # thus, not used in the view
            'email_verified': None,
            }


class EmailSchema(colander.MappingSchema):

    email = colander.SchemaNode(colander.String(), missing='')
    email_verified = colander.SchemaNode(colander.Boolean())


class BaseUserSchema(colander.MappingSchema):

    first_name = colander.SchemaNode(
        colander.String(),
        title=_('First name'),
        missing='',
        )
    last_name = colander.SchemaNode(
        colander.String(),
        title=_('Last name'),
        missing='',
        )
    screen_name = colander.SchemaNode(
        colander.String(),
        title=_('Screen name'),
        missing='',
        )


class UserSchema(BaseUserSchema):

    email = EmailSchema(
        title=_('Email'),
        widget=EmailWidget(),
        missing={'email': '', 'email_verified': False},
        )


class NewUserSchema(BaseUserSchema):

    email = colander.SchemaNode(
        colander.String(),
        title=_('Email'),
        missing='',
        )


class AccountDestroySchema(colander.MappingSchema):

    reason = colander.SchemaNode(
        colander.String(),
        missing='',
        title=_('Do you mind telling us your reasons? We want to get better!'),
        widget=TextAreaWidget(css_class='input-xlarge'),
        )


class UserPreferencesSchema(colander.MappingSchema):

    allow_google_analytics = colander.SchemaNode(
        colander.Boolean(),
        title=_('Allow statistics cookie'),
        missing=False,
        )
