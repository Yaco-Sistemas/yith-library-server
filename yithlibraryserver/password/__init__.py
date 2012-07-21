def includeme(config):
    config.add_route('password_collection_view', '/passwords')
    config.add_route('password_view', '/passwords/{password}')
