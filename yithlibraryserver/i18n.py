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

from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.threadlocal import get_current_request

translation_domain = 'yithlibraryserver'
TranslationString = TranslationStringFactory(translation_domain)


def deform_translator(term):
    return get_localizer(get_current_request()).translate(term)


def locale_negotiator(request):
    available_languages = request.registry.settings['available_languages']
    return request.accept_language.best_match(available_languages)
