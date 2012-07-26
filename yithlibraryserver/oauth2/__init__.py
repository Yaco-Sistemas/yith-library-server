def includeme(config):
    config.add_route('oauth2_applications', '/oauth2/applications')
    config.add_route('oauth2_application_new', '/oauth2/applications/new')
    config.add_route('oauth2_application_view', '/oauth2/applications/{app}')
    config.add_route('oauth2_application_delete', '/oauth2/applications/{app}/delete')

    config.add_route('oauth2_authorization_endpoint', '/oauth2/endpoints/authorization')
    config.add_route('oauth2_token_endpoint', '/oauth2/endpoints/token')
    config.add_route('oauth2_authorize_application', '/oauth2/authorizeapp/{app}')
    config.add_route('oauth2_authenticate_anonymous', '/oauth2/authenticate_anonymous/{app}')

    config.add_route('oauth2_revoke_application', '/oauth2/applications/{app}/revoke')
