import os.path

from yithlibraryserver import read_setting_from_env


def includeme(config):
    settings = config.registry.settings

    here = os.path.abspath(os.path.dirname(__file__))

    for key, default in (
        ('openid_url', 'https://www.google.com/accounts/o8/id'),
        ('openid_store_path', os.path.join(here, 'openid-store')),
        ):

        option = 'google_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    config.add_route('google_login', '/google/login')
    config.add_view('.views.google_login',
                    route_name='google_login', renderer='string')

    config.add_route('google_callback', '/google/callback')
    config.add_view('.views.google_callback',
                    route_name='google_callback', renderer='string')
