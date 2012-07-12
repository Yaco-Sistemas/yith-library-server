import hashlib
import hmac
import binascii
import random
import time
import urllib.parse

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.security import remember
from pyramid.view import view_config

import requests

from yithlibraryserver.twitter.users import get_user


#urllib.parse.quote('Dogs, Cats & Mice')

def quote(value):

    return urllib.parse.quote(value, safe='')


def nonce(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def timestamp():
    return int(time.time())


def sign(method, url, original_params, consumer_secret, oauth_token):
    # 1. create the parameter string
    param_string = '&'.join(['%s=%s' % (key, value) for key, value in sorted(original_params)])

    # 2. create signature base string
    signature_base = '%s&%s&%s' % (
        method.upper(), quote(url), quote(param_string),
        )

    # 3. create the signature key
    key = '%s&%s' % (quote(consumer_secret), quote(oauth_token))

    # 4. calculate the signature
    hashed = hmac.new(key.encode('ascii'),
                      signature_base.encode('ascii'),
                      hashlib.sha1)
    return quote(binascii.b2a_base64(hashed.digest())[:-1])


def auth_header(method, url, original_params, settings, oauth_token=''):
    params = list(original_params) + [
        ('oauth_consumer_key', settings['twitter.consumer_key']),
        ('oauth_nonce', nonce()),
        ('oauth_signature_method', 'HMAC-SHA1'),
        ('oauth_timestamp', str(timestamp())),
        ('oauth_version', '1.0'),
        ]
    params = [(quote(key), quote(value)) for key, value in params]

    signature = sign(method, url, params,
                     settings['twitter.consumer_secret'], oauth_token)
    params.append(('oauth_signature', signature))

    header = ", ".join(['%s="%s"' % (key, value) for key, value in params])

    return 'OAuth %s' % header


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

    user = get_user(request, user_id)
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
