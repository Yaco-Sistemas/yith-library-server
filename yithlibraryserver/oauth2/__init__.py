def includeme(config):
    config.add_route('oauth2_applications', '/oauth2/applications')
    config.add_route('oauth2_application_new', '/oauth2/applications/new')
    config.add_route('oauth2_application_view', '/oauth2/applications/{app}')
    config.add_route('oauth2_application_delete', '/oauth2/applications/{app}/delete')
