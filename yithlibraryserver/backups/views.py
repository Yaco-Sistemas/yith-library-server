# Yith Library Server is a password storage server.
# Copyright (C) 2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

import json

from pyramid.i18n import get_localizer
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from yithlibraryserver.backups.utils import get_backup_filename
from yithlibraryserver.backups.utils import get_user_passwords
from yithlibraryserver.i18n import translation_domain
from yithlibraryserver.i18n import TranslationString as _
from yithlibraryserver.password.models import PasswordsManager


@view_config(route_name='backups_index',
             renderer='templates/backups_index.pt',
             permission='backups')
def backups_index(request):
    return {}


@view_config(route_name='backups_export',
             renderer='json',
             permission='backups')
def backups_export(request):
    filename = get_backup_filename()
    request.response.content_disposition = 'attachment; filename=%s' % filename
    return get_user_passwords(request.db, request.user)


@view_config(route_name='backups_import',
             renderer='string',
             permission='backups')
def backups_import(request):
    response = HTTPFound(location=request.route_path('backups_index'))

    if 'passwords-file' in request.POST:
        passwords_field = request.POST['passwords-file']
        if passwords_field != '':
            try:
                raw_data = passwords_field.file.read().decode('utf-8')
                json_data = json.loads(raw_data)
                passwords_manager = PasswordsManager(request.db)
                passwords_manager.delete(request.user)
                passwords_manager.create(request.user, json_data)
            except ValueError:
                request.session.flash(
                    _('There was a problem reading your passwords file'),
                    'error')
                return response

            n_passwords = len(json_data)
            localizer = get_localizer(request)
            msg = localizer.pluralize(
                _('Congratulations, ${n_passwords} password has been imported'),
                _('Congratulations, ${n_passwords} passwords have been imported'),
                n_passwords,
                domain=translation_domain,
                mapping={'n_passwords': n_passwords},
                )
            request.session.flash(msg, 'success')
        else:
            request.session.flash(
                _('The passwords file is required to upload the passwords'),
                'error')
            return response
    else:
        request.session.flash(
            _('The passwords file is required to upload the passwords'),
            'error')
        return response

    return response
