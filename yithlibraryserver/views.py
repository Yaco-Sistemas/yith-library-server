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

from deform import Button, Form, ValidationFailure

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.view import view_config

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from yithlibraryserver.i18n import TranslationString as _
from yithlibraryserver.schemas import ContactSchema

log = logging.getLogger(__name__)


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {}


@view_config(route_name='contact', renderer='templates/contact.pt')
def contact(request):
    button1 = Button('submit', _('Send message'))
    button1.css_class = 'btn-primary'
    button2 = Button('cancel', _('Cancel'))
    button2.css_class = ''

    form = Form(ContactSchema(), buttons=(button1, button2))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        context = {'link': request.route_url('contact')}
        context.update(appstruct)

        text_body = render('yithlibraryserver:templates/email_contact.txt',
                           context, request=request)

        # chamaleon txt templates are rendered as utf-8 bytestrings
        text_body = text_body.decode('utf-8')

        html_body = render('yithlibraryserver:templates/email_contact.pt',
                           context, request=request)

        admin_emails = request.registry.settings['admin_emails']

        if admin_emails:
            message = Message(
                subject=("%s sent a message from Yith's contact form" %
                         appstruct['name']),
                recipients=request.registry.settings['admin_emails'],
                body=text_body,
                html=html_body,
                extra_headers={'Reply-To': appstruct['email']},
                )

            get_mailer(request).send(message)
        else:
            log.error(
                '%s <%s> tried to send a message from the contact form but no '
                'admin emails were configured. Message: %s' % (
                    appstruct['name'],
                    appstruct['email'],
                    appstruct['message'],
                    )
                )

        request.session.flash(
            _('Thank you very much for sharing your opinion'),
            'info',
            )

        return HTTPFound(location=request.route_path('home'))

    elif 'cancel' in request.POST:
        return HTTPFound(location=request.route_path('home'))

    initial = {}
    if request.user is not None:
        initial['name'] = request.user.get('first_name', '')
        if request.user.get('email_verified', False):
            initial['email'] = request.user.get('email', '')

    return {'form': form.render(initial)}


@view_config(route_name='tos', renderer='templates/tos.pt')
def tos(request):
    return {}
