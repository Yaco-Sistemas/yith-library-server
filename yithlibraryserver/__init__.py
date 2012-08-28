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

    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authorization_policy=ACLAuthorizationPolicy(),
        authentication_policy=AuthTktAuthenticationPolicy('seekrit'),
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
    config.include('yithlibraryserver.facebook')
    config.include('yithlibraryserver.oauth2')
    config.include('yithlibraryserver.password')
    config.include('yithlibraryserver.user')
    config.include('yithlibraryserver.twitter')

    config.add_route('home', '/')

    # Subscribers
    config.include('yithlibraryserver.subscribers')

    config.scan()
    return config.make_wsgi_app()
