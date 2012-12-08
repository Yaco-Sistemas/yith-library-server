# Yith Library Server is a password storage server.
# Copyright (C) 2012 Yaco Sistemas
# Copyright (C) 2012 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
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

import colander
from deform.widget import TextAreaWidget, TextInputWidget


class EmailWidget(TextInputWidget):

    email_verified_template = 'email_verified'

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (colander.null, None):
            cstruct = {'email': '', 'email_verified': False}

        email_output = super(EmailWidget, self).serialize(field,
                                                          cstruct['email'],
                                                          readonly)

        pstruct = field.schema.deserialize(cstruct)
        email_verified_output = field.renderer(
            self.email_verified_template,
            email_verified=pstruct['email_verified'],
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


class UserSchema(colander.MappingSchema):

    first_name = colander.SchemaNode(colander.String(), missing='')
    last_name = colander.SchemaNode(colander.String(), missing='')
    email = EmailSchema(
        widget=EmailWidget(),
        missing={'email': '', 'email_verified': False},
        )


class AccountDestroySchema(colander.MappingSchema):

    reason = colander.SchemaNode(
        colander.String(),
        missing='',
        title='Do you mind telling us your reasons? We want to get better!',
        widget=TextAreaWidget(css_class='input-xlarge'),
        )
