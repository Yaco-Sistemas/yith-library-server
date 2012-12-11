/*jslint nomen: true*/
// Yith Library Server is a password storage server.
// Copyright (C) 2012 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
//
// This file is part of Yith Library Server.
//
// Yith Library Server is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Yith Library Server is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.

(function ($) {
    "use strict";

    $.mozilla_persona = function (options) {
        var current_user = options.current_user,
            current_provider = options.current_provider;

        if (!current_user || current_provider !== 'persona') {
            current_user = null;
        }

        if (options.login_selector) {
            $(options.login_selector).click(function (event) {
                event.preventDefault();
                navigator.id.request();
            });
        }

        if (options.logout_selector) {
            $(options.logout_selector).click(function (event) {
                if (current_provider === 'persona') {
                    event.preventDefault();
                    navigator.id.logout();
                }
            });
        }

        navigator.id.watch({
            loggedInUser: current_user,
            onlogin: function (assertion) {
                var form = [
                    "<form class='hide' ",
                    "action='" + options.login_url + "' ",
                    "method='post'>",
                    "<input type='hidden' name='assertion' ",
                    "value='" + assertion + "'/>",
                    (options.next_url ? "<input type='hidden' name='next_url' value='" + options.next_url + "' />" : ""),
                    "</form>"
                ].join("");
                $(form).appendTo("body").submit();
            },
            onlogout: function () {
                if (typeof options.logout_url === 'string') {
                    window.location = options.logout_url;
                } else {
                    options.logout_url();
                }
            }
        });

    };

}(jQuery));
