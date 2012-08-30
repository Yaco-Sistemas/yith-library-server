from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPUnauthorized

import requests

from yithlibraryserver.compat import urlparse
from yithlibraryserver.twitter.authorization import auth_header
from yithlibraryserver.twitter.information import get_user_info
from yithlibraryserver.user.utils import split_name, register_or_update


def twitter_login(request):
    settings = request.registry.settings
    request_token_url = settings['twitter_request_token_url']
    oauth_callback_url = request.route_url('twitter_callback')

    params = (
        ('oauth_callback', oauth_callback_url),
        )

    auth = auth_header('POST', request_token_url, params, settings)

    response = requests.post(request_token_url, data='',
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    if response_args['oauth_callback_confirmed'] != 'true':
        return HTTPUnauthorized('oauth_callback_confirmed is not true')

    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    request.session['oauth_token'] = oauth_token
    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    authorize_url = '%s?oauth_token=%s' % (
        settings['twitter_authenticate_url'], oauth_token
        )
    return HTTPFound(location=authorize_url)


def twitter_callback(request):
    settings = request.registry.settings

    try:
        oauth_token = request.params['oauth_token']
    except KeyError:
        return HTTPBadRequest('Missing required oauth_token')

    try:
        oauth_verifier = request.params['oauth_verifier']
    except KeyError:
        return HTTPBadRequest('Missing required oauth_verifier')

    try:
        saved_oauth_token = request.session['oauth_token']
    except KeyError:
        return HTTPBadRequest('No oauth_token was found in the session')

    if saved_oauth_token != oauth_token:
        return HTTPUnauthorized("OAuth tokens don't match")
    else:
        del request.session['oauth_token']

    access_token_url = settings['twitter_access_token_url']

    params = (
        ('oauth_token', oauth_token),
        )

    auth = auth_header('POST', access_token_url, params, settings, oauth_token)

    response = requests.post(access_token_url,
                             data='oauth_verifier=%s' % oauth_verifier,
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    user_id = response_args['user_id']

    info = get_user_info(settings, user_id, oauth_token)
    first_name, last_name = split_name(info['name'])

    return register_or_update(request, 'twitter', user_id, {
            'screen_name': response_args['screen_name'],
            'first_name': first_name,
            'last_name': last_name,
            }, request.route_path('home'))
