import urllib.parse

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.security import remember
from pyramid.view import view_config

import requests

from yithlibraryserver.twitter.authorization import auth_header


@view_config(route_name='twitter_login', renderer='string')
def twitter_login(request):
    settings = request.registry.settings
    request_token_url = settings['twitter.request_token_url']
    oauth_callback_url = request.route_url('twitter_callback')

    params = (
        ('oauth_callback', oauth_callback_url),
        )

    auth = auth_header('POST', request_token_url, params, settings)

    response = requests.post(request_token_url, data='',
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urllib.parse.parse_qsl(response.text))
    if response_args['oauth_callback_confirmed'] != 'true':
        return HTTPUnauthorized('oauth_callback_confirmed is not true')

    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    request.session['oauth_token'] = oauth_token

    authorize_url = '%s?oauth_token=%s' % (
        settings['twitter.authenticate_url'], oauth_token
        )
    return HTTPFound(location=authorize_url)


@view_config(route_name='twitter_callback', renderer='string')
def twitter_callback(request):
    settings = request.registry.settings

    oauth_token = request.params['oauth_token']
    oauth_verifier = request.params['oauth_verifier']

    saved_oauth_token = request.session['oauth_token']
    if saved_oauth_token != oauth_token:
        return HTTPUnauthorized("OAuth tokens don't match")
    else:
        del request.session['oauth_token']

    access_token_url = settings['twitter.access_token_url']

    params = (
        ('oauth_token', oauth_token),
        )

    auth = auth_header('POST', access_token_url, params, settings, oauth_token)

    response = requests.post(access_token_url, #'http://localhost:9000',
                             data='oauth_verifier=%s' % oauth_verifier,
                             headers={'Authorization': auth})

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)


    response_args = dict(urllib.parse.parse_qsl(response.text))
    #oauth_token_secret = response_args['oauth_token_secret']
    oauth_token = response_args['oauth_token']
    user_id = response_args['user_id']
    screen_name = response_args['screen_name']

    user = request.db.users.find_one({'provider_user_id': user_id})
    if user is None:
        remember_headers = remember(request, user_id)
        next_url = request.route_url('register_new_user')
        next_url += '?' + urllib.parse.urlencode({
            'screen_name': screen_name,
            })
        return HTTPFound(location=next_url,
                         headers=remember_headers)
    else:
        remember_headers = remember(request, str(user['_id']))
        next_url = request.route_url('oauth2_applications')
        return HTTPFound(location=next_url,
                         headers=remember_headers)
