.. _configuration_chapter:

Configuring :program:`Yith Library Server`
==========================================

How the configuration is read
-----------------------------

:program:`Yith Library Server` read its configuration options from
two different sources:

- A configuration file with a INI syntax
- Environment variables. This work for many options but not all of them.

If an option is defined both in the configuration file and an
environment variable, :program:`Yith Library Server` will use the
value of the environment variable.

:program:`Yith Library Server` comes with two configuration
templates, one for development and one for production purposes.
You should copy one of these templates instead of editing them
because that would make the upgrade process easier.

The development template is named :file:`development.ini` and the
production template is named :file:`production.ini`. These templates
have plenty of comments so it should not be very hard to get
started with them.

Once you have your configuration options established in a
configuration file you can run :program:`Yith Library Server`
using the following command:

.. code-block:: text

   pserve configuration_file.ini
     Starting server in PID 6743.
     serving on http://0.0.0.0:6543


Configuration options
---------------------

Authentication
~~~~~~~~~~~~~~

:program:`Yith Library Server` uses a secret value to sign the
authentication ticket cookie, which is used to keep track of the
authentication status of the current user.

It is extremely important that **this value is kept secret**. This
is a required value with an empty default value. This means that
you need to set it before running the server. The
:file:`development.ini` template has a value of ``1234`` for this
option so you can get your server running as fast as possible
without worrying about these things.

.. code-block:: ini

   auth_tk_secret = komb81v1mi1t9fsia9q22sg3wobylz88

In this example, the auth_tk_secret value has been generated
with the following command in a Unix shell:

.. code-block:: text

   $ tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null;echo


You can also set this option with an environment variable:

.. code-block:: bash

   $ export AUTH_TK_SECRET=komb81v1mi1t9fsia9q22sg3wobylz88


Available languages
~~~~~~~~~~~~~~~~~~~

This option defines the set of available languages that
:program:`Yith Library Server` will use for internationalization
purposes. The value is a space delimited list of iso codes.

.. code-block:: ini

   available_languages = en es

The default value for this option is ``en es``, which means
there is support for English and Spanish.

As of this writing only English and Spanish translation of UI
text messages are available. With this configuration option
you can restrict the set of available languages but it you add
new languages to it, their translatation catalogs will not be
generated magically.

This option does not have a environment variable. You can only
set it with a configuration file.

CORS support
~~~~~~~~~~~~

:abbr:`CORS (Cross-Origin resource sharing)` is useful when a browser
based client wants to communicate with :program:`Yith Library Server`.
Using this setting you can define a whitelist of allowed hosts to
whom you want to allow access from the server.

The syntax is a space separated list of URLs:

.. code-block:: ini

   cors_allowed_origins = http://localhost https://localhost

Note that if you want to allow access from HTTP and HTTPS both
URLs need to be defined.

You can also set this option with an environment variable:

.. code-block:: bash

   $ export CORS_ALLOWED_ORIGINS="http://localhost https://localhost"

The default value for this option is the empty list.

Database
~~~~~~~~

Chaging this setting you can customize your database location and
access settings.

The syntax is defined in MongoDB reference documentation as the
`Connection String URI Format <http://docs.mongodb.org/manual/reference/connection-string/>`_

.. code-block:: ini

   mongo_uri = mongodb://localhost:27017/yith-library

You can also set this option with an environment variable:

.. code-block:: bash

   $ export MONGO_URI=mongodb://localhost:27017/yith-library

The default value for this option is ``mongodb://localhost:27017/yith-library``

Facebook authentication
~~~~~~~~~~~~~~~~~~~~~~~

You can configure support for Facebook authentication in
:program:`Yith Library Server` by defining several settings. If you
do so, your users will be able to access your server authenticating
themselves via Facebook.

But first you need to create a Facebook application at
https://developers.facebook.com/apps . The type of Facebook application
is **Website with Facebook Login** and you need to enter your server
URL, e.g. http://localhost:65432/

After you have created and configured the Facebook application you
are ready to fill the settings in :program:`Yith Library Server`.

The first setting is ``facebook_app_id`` and is a number you can
obtain from your App summary page at Facebook.

.. code-block:: ini

   facebook_app_id = 123456789012345

Then, there is ``facebook_app_secret`` which is the secret part of
Facebook client credentials. You can also obtain it from your
App summary page at Facebook.

.. code-block:: ini

   facebook_app_secret = 1234567890abcdef1234567890abcdef

There are no default values for the settings ``facebook_app_id``
and ``facebook_app_secret``. If they are not set, Facebook
authentication is automatically disabled.

.. warning::

   It is perfectly fine to avoid Facebook authentication but it is
   actually required to enable at least one of the supported
   authentication mechanisms (Facebook, Google, Twitter or Persona).
   Otherwise your users won't be able to access your server.

There are three more Facebook settings that are used to perform the
actual authentication but they have good default values and you
should only need to change them if Facebook itself changes them.
These are the settings and their default values:

.. code-block:: ini

   facebook_dialog_oauth_url = https://www.facebook.com/dialog/oauth/
   facebook_access_token_url = https://graph.facebook.com/oauth/access_token
   facebook_basic_information_url = https://graph.facebook.com/me

You can also set these options with environment variables:

.. code-block:: bash

   $ export FACEBOOK_APP_ID="123456789012345"
   $ export FACEBOOK_APP_SECRET="1234567890abcdef1234567890abcdef"
   $ export FACEBOOK_DIALOG_OAUTH_URL="https://www.facebook.com/dialog/oauth/"
   $ export FACEBOOK_ACCESS_TOKEN_URL="https://graph.facebook.com/oauth/access_token"
   $ export FACEBOOK_BASIC_INFORMATION_URL="https://graph.facebook.com/me"

Google Analytics support
~~~~~~~~~~~~~~~~~~~~~~~~
This is an optional settings to enable Google Analytics in
:program:`Yith Library Server`. Before you configure it you have
to add your server URL into
`Google Analytics <http://www.google.com/analytics/>`_ and obtain
the code they give you to add the Javascript snippet.

After that, you are ready to configure this setting:

.. code-block:: ini

   google_analytis_code = UA-12345678-2

You can also set this option with an environment variable:

.. code-block:: bash

   $ export GOOGLE_ANALYTICS_CODE="UA-12345678-2"

There is no default value for this setting. If unset, the Javascript
snippet for Google Analytics will not be rendered in the final HTML
of your server.


Google authentication
~~~~~~~~~~~~~~~~~~~~~

You can configure support for Google authentication in
:program:`Yith Library Server` by defining several settings. If you
do so, your users will be able to access your server authenticating
themselves via Google.

But first you need to create a Google application at
https://code.google.com/apis/console?hl=es#access . Your need to
enter the Redirect URI and the Javascript origin. If your server is
located at http://localhost:65432/ then that is the value for the
Javascript origin and your redirect URI would be
http://localhost:65432/google/callback

After you have created and configured the Google application you
are ready to fill the settings in :program:`Yith Library Server`.

The first setting is ``facebook_client_id`` and is a number you can
obtain from your API Access page at Google.

.. code-block:: ini

   google_client_id = 123456789012.apps.googleusercontent.com

Then, there is ``google_client_secret`` which is the secret part of
Google client credentials. You can also obtain it from your
API Access page at Google.

.. code-block:: ini

   google_client_secret = 1234567890abcdefghijklmn

There are no default values for the settings ``google_client_id``
and ``google_client_secret``. If they are not set, Google
authentication is automatically disabled.

.. warning::

   It is perfectly fine to avoid Google authentication but it is
   actually required to enable at least one of the supported
   authentication mechanisms (Facebook, Google, Twitter or Persona).
   Otherwise your users won't be able to access your server.

There are three more Google settings that are used to perform the
actual authentication but they have good default values and you
should only need to change them if Google itself changes them.
These are the settings and their default values:

.. code-block:: ini

   google_auth_uri = https://accounts.google.com/o/oauth2/auth
   google_token_uri = https://accounts.google.com/o/oauth2/token
   google_user_info_uri = https://www.googleapis.com/oauth2/v1/userinfo

You can also set these options with environment variables:

.. code-block:: bash

   $ export GOOGLE_CLIENT_ID="123456789012.apps.googleusercontent.com"
   $ export GOOGLE_CLIENT_SECRET="1234567890abcdefghijklmn"
   $ export GOOGLE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
   $ export GOOGLE_TOKEN_URI="https://accounts.google.com/o/oauth2/token"
   $ export GOOGLE_USER_INFO_URI="https://www.googleapis.com/oauth2/v1/userinfo"

.. todo::
   Logging

.. todo::
   Mail

Persona authentication
~~~~~~~~~~~~~~~~~~~~~~

You can configure support for Mozilla Persona authentication in
:program:`Yith Library Server` by defining several settings. If you
do so, your users will be able to access your server authenticating
themselves via Persona.

The first setting is ``persona_audience`` and it should be the full
URL of your server, including the port.

.. code-block:: ini

   persona_audience = http://localhost:80

There are no default value for the¡s setting. If it is not set,
Persona authentication is automatically disabled.

.. warning::

   It is perfectly fine to avoid Persona authentication but it is
   actually required to enable at least one of the supported
   authentication mechanisms (Facebook, Google, Twitter or Persona).
   Otherwise your users won't be able to access your server.

There is one more Persona seetting that is used to verify the
assertion that Persona sends to :program:`Yith Library Server`.
It has a good default value and you should only need to change
it if Persona itself change it:

.. code-block:: ini

   persona_verifier_url = https://verifier.login.persona.org/verify

You can also set these options with environment variables:

.. code-block:: bash

   $ export PERSONA_AUDIENCE="http://localhost:80"
   $ export PERSONA_VERIFIER_URL="https://verifier.login.persona.org/verify"

.. todo::
   Sessions

Twitter authentication
~~~~~~~~~~~~~~~~~~~~~~

You can configure support for Twitter authentication in
:program:`Yith Library Server` by defining several settings. If you
do so, your users will be able to access your server authenticating
themselves via Twitter.

But first you need to create a Twitter application at
https://dev.twitter.com/apps/new . Your need to
enter the Website and Callback URL. If your server is
located at http://localhost:65432/ then that is the value for the
Website your redirect URI would be http://localhost:65432/twitter/callback

After you have created and configured the Twitter application you
are ready to fill the settings in :program:`Yith Library Server`.

The first setting is ``twitter_consumer_key`` and is a string you can
obtain from your App page at Twitter.

.. code-block:: ini

   twitter_consumer_key = 1234567890abcdefghij

Then, there is ``twitter_consumer_secret`` which is the secret part of
Twitter client credentials. You can also obtain it from your
App page at Twitter.

.. code-block:: ini

   twitter_consumer_secret = 1234567890abcdefghijklmnopqrstuvwxyzABCDE

There are no default values for the settings ``twitter_consumer_key``
and ``twitter_consumer_secret``. If they are not set, Twitter
authentication is automatically disabled.

.. warning::

   It is perfectly fine to avoid Twitter authentication but it is
   actually required to enable at least one of the supported
   authentication mechanisms (Facebook, Google, Twitter or Persona).
   Otherwise your users won't be able to access your server.

There are three more Twitter settings that are used to perform the
actual authentication but they have good default values and you
should only need to change them if Twitter itself changes them.
These are the settings and their default values:

.. code-block:: ini

   twitter_request_token_url = https://api.twitter.com/oauth/request_token
   twitter_authenticate_url = https://api.twitter.com/oauth/authenticate
   twitter_access_token_url = https://api.twitter.com/oauth/access_token

You can also set these options with environment variables:

.. code-block:: bash

   $ export TWITTER_CONSUMER_KEY="1234567890abcdefghij"
   $ export TWITTER_CONSUMER_SECRET="1234567890abcdefghijklmnopqrstuvwxyzABCDE"
   $ export TWITTER_REQUEST_TOKEN_URL="https://api.twitter.com/oauth/request_token"
   $ export TWITTER_AUTHENTICATE_URL="https://api.twitter.com/oauth/authenticate"
   $ export TWITTER_ACCESS_TOKEN_URL="https://api.twitter.com/oauth/access_token"
