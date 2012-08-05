from yithlibraryserver import read_setting_from_env

def includeme(config):
    settings = config.registry.settings
    for key, default in (
        ('app_id', None),
        ('app_secret', None),
        ('dialog_oauth_url', 'https://www.facebook.com/dialog/oauth/'),
        ('access_token_url', 'https://graph.facebook.com/oauth/access_token'),
        ('basic_information_url', 'https://graph.facebook.com/me'),
        ):
        option = 'facebook_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    if settings['facebook_app_id'] and settings['facebook_app_secret']:
        config.add_route('facebook_login', '/facebook/login')
        config.add_view('.views.facebook_login',
                        route_name='facebook_login', renderer='string')
        config.add_route('facebook_callback', '/facebook/callback')
        config.add_view('.views.facebook_callback',
                        route_name='facebook_callback', renderer='string')
