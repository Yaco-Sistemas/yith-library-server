
# Yith Library Server is a password storage server.
# Copyright (C) 2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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
        ('user', 'sdk-three_api1.sdk.com'),
        ('password', 'QFZCWN5HZM8VBG7Q'),
        ('signature', 'A-IzJhZZjhg29XQ2qnhapuwxIDzyAZQ92FRP5dqBzVesOkzbdUONzmOU'),
        ('nvp_url', 'https://api-3t.sandbox.paypal.com/nvp'),
        ('express_checkout_url', 'https://www.sandbox.paypal.com/webscr')
    ):
        option = 'paypal_%s' % key
        settings[option] = read_setting_from_env(settings, option, default)

    config.add_route('contributions_index', '/contribute')
    config.add_route('contributions_donate', '/contribute/donate')
    config.add_route('contributions_paypal_success_callback',
                     '/contribute/paypal-success-callback')
    config.add_route('contributions_paypal_cancel_callback',
                     '/contribute/paypal-cancel-callback')
