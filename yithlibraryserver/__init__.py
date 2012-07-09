from pyramid.config import Configurator
from pyramid.events import NewRequest

from yithlibraryserver.cors import CORSManager
from yithlibraryserver.db import MongoDB


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Mongodb setup
    mongodb = MongoDB(settings.get('mongo_uri'))
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
    config.add_route('password_collection_view', '/{user}')
    config.add_route('password_view', '/{user}/{password}')

    config.scan()
    return config.make_wsgi_app()
