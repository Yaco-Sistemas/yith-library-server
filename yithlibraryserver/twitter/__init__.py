from yithlibraryserver import read_setting_from_env

def includeme(config):
    settings = config.registry.settings
    for key, default in (
        ('consumer_key', None),
        ('consumer_secret', None),
        ('request_token_url', 'https://api.twitter.com/oauth/request_token'),
        ('authenticate_url', 'https://api.twitter.com/oauth/authenticate'),
        ('access_token_url', 'https://api.twitter.com/oauth/access_token'),
        ):
        option = 'twitter_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    if settings['twitter_consumer_key'] and settings['twitter_consumer_secret']:
        config.add_route('twitter_login', '/twitter/login')
        config.add_view('.views.twitter_login',
                        route_name='twitter_login', renderer='string')
        config.add_route('twitter_callback', '/twitter/callback')
        config.add_view('.views.twitter_callback',
                        route_name='twitter_callback', renderer='string')
