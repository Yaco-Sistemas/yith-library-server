from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from yithlibraryserver.config import read_setting_from_env
from yithlibraryserver.cors import CORSManager
from yithlibraryserver.db import MongoDB
from yithlibraryserver.security import RootFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authorization_policy=ACLAuthorizationPolicy(),
        authentication_policy=AuthTktAuthenticationPolicy('seekrit'),
        )
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Beaker (sessions) setup
    config.include('pyramid_beaker')

    # Mongodb setup
    mongodb = MongoDB(read_setting_from_env(settings, 'mongo_uri'))
    config.registry.settings['db_conn'] = mongodb.get_connection()

    def add_mongo_db(event):
        event.request.db = mongodb.get_database()

    config.add_subscriber(add_mongo_db, NewRequest)

    # CORS support setup
    cors_manager = CORSManager(settings.get('cors_allowed_origins', ''))
    def add_cors_headers_response(event):
        def cors_headers_callback(request, response):
            return cors_manager.add_cors_header(request, response)
        event.request.add_response_callback(cors_headers_callback)
    config.add_subscriber(add_cors_headers_response, NewRequest)

    # Routes
    config.include('yithlibraryserver.oauth2')
    config.include('yithlibraryserver.password')
    config.include('yithlibraryserver.user')
    config.include('yithlibraryserver.twitter')

    config.add_route('home', '/')

    config.scan()
    return config.make_wsgi_app()
