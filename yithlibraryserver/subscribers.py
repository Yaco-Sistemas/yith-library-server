from pyramid.events import BeforeRender, NewRequest
from pyramid.renderers import get_renderer

from yithlibraryserver.db import get_db
from yithlibraryserver.user.security import get_user


def add_cors_headers_response(event):
    cors_manager = event.request.registry.settings['cors_manager']

    def cors_headers_callback(request, response):
        return cors_manager.add_cors_header(request, response)

    event.request.add_response_callback(cors_headers_callback)


def add_base_template(event):
    base_renderer = get_renderer('yithlibraryserver:templates/base.pt')
    event.update({'base': base_renderer.implementation()})


def includeme(config):
    config.set_request_property(get_db, 'db', reify=True)
    config.set_request_property(get_user, 'user', reify=True)

    config.add_subscriber(add_cors_headers_response, NewRequest)
    config.add_subscriber(add_base_template, BeforeRender)
