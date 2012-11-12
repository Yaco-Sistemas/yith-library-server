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

import re

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from yithlibraryserver.config import read_setting_from_env
from yithlibraryserver.cors import CORSManager
from yithlibraryserver.db import MongoDB
from yithlibraryserver.security import RootFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # read pyramid_mailer options
    for key in ('host', 'port', 'username', 'password', 'default_sender'):
        option = 'mail_' + key
        settings[option] = read_setting_from_env(settings, option)

    # read admin_emails option
    settings['admin_emails'] = read_setting_from_env(settings, 'admin_emails')
    if settings['admin_emails'] is not None:
        settings['admin_emails'] = settings['admin_emails'].split()

    # read Google Analytics code
    settings['google_analytics_code'] = read_setting_from_env(settings, 'google_analytics_code', None)

    # main config object
    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authorization_policy=ACLAuthorizationPolicy(),
        authentication_policy=AuthTktAuthenticationPolicy('seekrit', wild_domain=False),
        )
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Beaker (sessions) setup
    config.include('pyramid_beaker')

    # Mailer setup
    if 'testing' in settings and settings['testing'] is True:
        config.include('pyramid_mailer.testing')
    else:  # pragma: no cover
        config.include('pyramid_mailer')
    config.include('pyramid_tm')

    # Mongodb setup
    mongodb = MongoDB(read_setting_from_env(settings, 'mongo_uri'))
    config.registry.settings['mongodb'] = mongodb
    config.registry.settings['db_conn'] = mongodb.get_connection()

    # CORS support setup
    config.registry.settings['cors_manager'] = CORSManager(
        read_setting_from_env(settings, 'cors_allowed_origins', ''))

    # Routes
    config.include('yithlibraryserver.oauth2')
    config.include('yithlibraryserver.password')

    # the user package needs to be included before twitter,
    # facebook and google
    config.include('yithlibraryserver.user')

    config.include('yithlibraryserver.twitter')
    config.include('yithlibraryserver.facebook')
    config.include('yithlibraryserver.google')

    includeme(config)

    # Subscribers
    config.include('yithlibraryserver.subscribers')

    config.scan(ignore=[re.compile('.*tests.*').search, '.testing'])
    return config.make_wsgi_app()


def includeme(config):
    config.add_route('home', '/')
    config.add_route('tos', '/tos')
