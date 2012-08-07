from pkg_resources import resource_filename
from deform import Form

from pyramid.path import AssetResolver

def includeme(config):
    # override deform templates
    deform_templates = resource_filename('deform', 'templates')
    resolver = AssetResolver('yithlibraryserver.oauth2')
    search_path = (resolver.resolve('templates').abspath(), deform_templates)
    Form.set_zpt_renderer(search_path)

    config.add_route('oauth2_applications', '/oauth2/applications')
    config.add_route('oauth2_application_new', '/oauth2/applications/new')
    config.add_route('oauth2_application_edit', '/oauth2/applications/{app}/edit')
    config.add_route('oauth2_application_delete', '/oauth2/applications/{app}/delete')

    config.add_route('oauth2_authorization_endpoint', '/oauth2/endpoints/authorization')
    config.add_route('oauth2_token_endpoint', '/oauth2/endpoints/token')

    config.add_route('oauth2_revoke_application', '/oauth2/applications/{app}/revoke')
