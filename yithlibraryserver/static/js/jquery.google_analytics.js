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

    var _gaq;

    if (window._gaq === undefined) {
        _gaq = window._gaq = [];
    }

    $.google_analytics = (function () {
        var _account;

        return {
            init: function (account) {
                _account = account;
            },

            show: function () {
                var ga = document.createElement('script'),
                    script = document.getElementsByTagName('script')[0];

                _gaq.push(['_setAccount', _account]);
                _gaq.push(['_trackPageview']);

                ga.type = 'text/javascript';
                ga.async = true;
                ga.src = ('https:' === document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
                script.parentNode.insertBefore(ga, script);
            },

            send_preference: function (allow, $form) {
                var self = this;
                $.ajax({
                    type: $form.attr('method'),
                    url: $form.attr('action'),
                    data: allow,
                    success: function (data) {
                        $form.parent('.alert').slideUp();
                        if (data.allow) {
                            self.show();
                        }
                    }
                });
            }
        };
    }());

    $('#google-analytics-preference-form')
        .find('[name="yes"]').click(function (event) {
            event.preventDefault();
            $.google_analytics.send_preference(
                {'yes': $(this).val()},
                $('#google-analytics-preference-form')
            );
        })
        .end()
        .find('[name="no"]').click(function (event) {
            event.preventDefault();
            $.google_analytics.send_preference(
                {'no': $(this).val()},
                $('#google-analytics-preference-form')
            );
        });

}(jQuery));
