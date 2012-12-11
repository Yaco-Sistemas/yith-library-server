(function ($) {
    "use strict";
    $(document).ready(function () {
        var $form = $("#persona-login-form"),
            current_user = $form.attr("data-current-user"),
            current_provider = $form.attr("data-current-provider"),
            logout_url = $(".logout").attr("href");

        if (!current_user || current_provider !== 'persona') {
            // Persona needs null, not undefined or false or 0
            current_user = null;
        }

        $(".persona-login-btn").click(function (event) {
            event.preventDefault();
            navigator.id.request();
        });

        $(".logout").click(function (event) {
            if (current_provider === 'persona') {
                event.preventDefault();
                navigator.id.logout();
            }
        });

        navigator.id.watch({
            loggedInUser: current_user,
            onlogin: function (assertion) {
                $form.find('[name="assertion"]').val(assertion);
                $form.submit();
            },
            onlogout: function () {
                if (logout_url !== undefined) {
                    window.location = logout_url;
                }
            }
        });
    });
}(jQuery));
