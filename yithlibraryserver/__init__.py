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

import re

from pkg_resources import resource_filename
from deform import Form
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import ConfigurationError
from pyramid.path import AssetResolver
from pyramid.settings import asbool

from yithlibraryserver.config import read_setting_from_env
from yithlibraryserver.cors import CORSManager
from yithlibraryserver.db import MongoDB
from yithlibraryserver.jsonrenderer import json_renderer
from yithlibraryserver.i18n import deform_translator, locale_negotiator
from yithlibraryserver.security import RootFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # read pyramid_mailer options
    for key, default in (
        ('host', 'localhost'),
        ('port', '25'),
        ('username', None),
        ('password', None),
        ('default_sender', 'no-reply@yithlibrary.com')
        ):
        option = 'mail_' + key
        settings[option] = read_setting_from_env(settings, option, default)

    # read admin_emails option
    settings['admin_emails'] = read_setting_from_env(settings, 'admin_emails', '').split()

    # read Google Analytics code
    settings['google_analytics_code'] = read_setting_from_env(
        settings, 'google_analytics_code', None)

    # read the auth secret
    settings['auth_tk_secret'] = read_setting_from_env(
        settings, 'auth_tk_secret', None)
    if settings['auth_tk_secret'] is None:
        raise ConfigurationError('The auth_tk_secret configuration '
                                 'option is required')

    # read the Mongodb URI
    settings['mongo_uri'] = read_setting_from_env(settings, 'mongo_uri', None)
    if settings['mongo_uri'] is None:
        raise ConfigurationError('The mongo_uri configuration '
                                 'option is required')

    # Available languages
    available_languages = read_setting_from_env(settings, 'available_languages', 'en es')

    settings['available_languages'] = [
        lang for lang in available_languages.split(' ') if lang
        ]

    # Public URL root
    settings['public_url_root'] = read_setting_from_env(
        settings, 'public_url_root', 'http://localhost:6543/')

    # Google and Facebook settings for pyramid_sna
    settings['google_scope'] = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
    settings['google_callback'] = 'yithlibraryserver.sna_callbacks.google_callback'
    settings['facebook_scope'] = 'email'
    settings['facebook_callback'] = 'yithlibraryserver.sna_callbacks.facebook_callback'

    # main config object
    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authorization_policy=ACLAuthorizationPolicy(),
        authentication_policy=AuthTktAuthenticationPolicy(
            settings['auth_tk_secret'],
            wild_domain=False,
            hashalg='sha512',
            ),
        locale_negotiator=locale_negotiator,
        )
    config.add_renderer('json', json_renderer)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Beaker (sessions) setup
    config.include('pyramid_beaker')

    # Mailer setup
    if 'testing' in settings and asbool(settings['testing']):
        config.include('pyramid_mailer.testing')
        config.include('yithlibraryserver.datetimeservice.testing')
    else:  # pragma: no cover
        config.include('pyramid_mailer')
        config.include('yithlibraryserver.datetimeservice')

    # Google/Facebook authentication
    config.include('pyramid_sna')

    config.include('pyramid_tm')

    # Mongodb setup
    mongodb = MongoDB(settings['mongo_uri'])
    config.registry.settings['mongodb'] = mongodb
    config.registry.settings['db_conn'] = mongodb.get_connection()

    # CORS support setup
    config.registry.settings['cors_manager'] = CORSManager(
        read_setting_from_env(settings, 'cors_allowed_origins', ''))

    # Routes
    config.include('yithlibraryserver.backups')
    config.include('yithlibraryserver.contributions')
    config.include('yithlibraryserver.oauth2')
    config.include('yithlibraryserver.password')

    # Translation directories
    config.add_translation_dirs('yithlibraryserver:locale/')

    # the user package needs to be included before twitter,
    # facebook and google
    config.include('yithlibraryserver.user')

    config.include('yithlibraryserver.twitter')

    if config.registry.settings['facebook_auth_enabled']:
        config.add_identity_provider('facebook')

    if config.registry.settings['google_auth_enabled']:
        config.add_identity_provider('google')

    config.include('yithlibraryserver.persona')

    includeme(config)

    # Subscribers
    config.include('yithlibraryserver.subscribers')

    config.scan(ignore=[re.compile('.*tests.*').search,
                        re.compile('.*testing.*').search])
    return config.make_wsgi_app()


def includeme(config):
    # override deform templates
    deform_templates = resource_filename('deform', 'templates')
    resolver = AssetResolver('yithlibraryserver')
    search_path = (
        resolver.resolve('templates').abspath(),
        deform_templates,
        )

    Form.set_zpt_renderer(search_path, translator=deform_translator)

    config.add_route('home', '/')
    config.add_route('contact', '/contact')
    config.add_route('tos', '/tos')
    config.add_route('faq', '/faq')
