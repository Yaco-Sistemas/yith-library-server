# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012-2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of Yith Library Server.
#
# Yith Library Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yith Library Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.

from yithlibraryserver import read_setting_from_env


def includeme(config):
    settings = config.registry.settings
    for key, default in (
        ('consumer_key', None),
        ('consumer_secret', None),
        ('request_token_url', 'https://api.twitter.com/oauth/request_token'),
        ('authenticate_url', 'https://api.twitter.com/oauth/authenticate'),
        ('access_token_url', 'https://api.twitter.com/oauth/access_token'),
        ('user_info_url', 'https://api.twitter.com/1/users/show.json'),
       ):
        option = 'twitter_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    if (settings['twitter_consumer_key']
        and settings['twitter_consumer_secret']):

        config.add_route('twitter_login', '/twitter/login')
        config.add_view('.views.twitter_login',
                        route_name='twitter_login', renderer='string')
        config.add_route('twitter_callback', '/twitter/callback')
        config.add_view('.views.twitter_callback',
                        route_name='twitter_callback', renderer='string')

        config.add_identity_provider('twitter')
