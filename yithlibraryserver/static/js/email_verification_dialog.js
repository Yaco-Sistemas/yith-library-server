(function ($) {
    "use strict";
    $(document).ready(function () {
        $("#send-verification-email").click(function (event) {
            var $button = $(this);
            event.preventDefault();

            if ($button.hasClass("disabled")) {
                return;
            }
            $button.addClass("disabled");
            $.ajax({
                type: 'POST',
                url: $button.attr("href"),
                data: {submit: 'Send verification code'},
                dataType: 'json',
                success: function (data, textStatus, jqXHR) {
                    if (data.status === 'ok') {
                        $("#email-verification-dialog .alert-info").removeClass("hide");
                        $("#open-email-verification-dialog").addClass("hide");
                    } else {
                        $("#email-verification-dialog .alert-error").removeClass("hide").find("strong").text(data.error);
                        $("#email-verification-dialog .alert-info").addClass("hide");
                        $button.removeClass("disabled");
                    }
                }
            });
        });
    });
}(jQuery));
