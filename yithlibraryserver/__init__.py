from pyramid.config import Configurator
from pyramid.events import NewRequest

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

    # Routes
    config.add_route('home', '/')

    config.scan()
    return config.make_wsgi_app()
