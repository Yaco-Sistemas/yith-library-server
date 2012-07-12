def includeme(config):
    config.add_route('twitter_login', '/twitter/login')
    config.add_route('twitter_callback', '/twitter/callback')
