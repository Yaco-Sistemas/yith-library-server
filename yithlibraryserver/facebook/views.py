import uuid

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPUnauthorized
from pyramid.security import remember

import requests

from yithlibraryserver.compat import urlparse, url_encode
from yithlibraryserver.facebook.information import get_user_info
from yithlibraryserver.user.utils import update_user


def facebook_login(request):
    settings = request.registry.settings
    redirect_url = request.route_url('facebook_callback')

    state = str(uuid.uuid4())
    request.session['state'] = state

    params = {
        'client_id': settings['facebook_app_id'],
        'redirect_uri': redirect_url,
        'scope': 'email',
        'state': state,
        }

    dialog_url = settings['facebook_dialog_oauth_url']
    url = dialog_url + '?' + url_encode(params)

    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    return HTTPFound(location=url)


def facebook_callback(request):
    settings = request.registry.settings

    try:
        code = request.params['code']
    except KeyError:
        return HTTPBadRequest('Missing required code')

    try:
        state = request.params['state']
    except KeyError:
        return HTTPBadRequest('Missing required state')

    try:
        my_state = request.session['state']
        if state != my_state:
            return HTTPUnauthorized('State parameter does not match internal state. You may be a victim of CSRF')
        else:
            del request.session['state']
    except KeyError:
        return HTTPUnauthorized('Missing internal state. You may be a victim of CSRF')

    params = {
        'client_id': settings['facebook_app_id'],
        'client_secret': settings['facebook_app_secret'],
        'redirect_uri': request.route_url('facebook_callback'),
        'code': code,
        }

    access_token_url = '%s?%s' % (
        settings['facebook_access_token_url'],
        url_encode(params),
        )
    response = requests.get(access_token_url)

    if response.status_code != 200:
        return HTTPUnauthorized(response.text)

    response_args = dict(urlparse.parse_qsl(response.text))
    access_token = response_args['access_token']
    #expires = response_args['expires']

    # get basic information about the user
    info = get_user_info(request, access_token)
    user_id = info['id']

    if 'next_url' in request.session:
        next_url = request.session['next_url']
        del request.session['next_url']
    else:
        next_url = request.route_path('home')

    user = request.db.users.find_one({'facebook_id': user_id})
    if user is None:
        request.session['user_info'] = {
            'provider': 'facebook',
            'facebook_id': user_id,
            'screen_name': info['username'],
            'first_name': info['first_name'],
            'last_name': info['last_name'],
            'email': info['email'],
            }
        request.session['next_url'] = next_url
        return HTTPFound(location=request.route_path('register_new_user'))
    else:
        update_user(request, user, info)
        remember_headers = remember(request, str(user['_id']))
        return HTTPFound(location=next_url,
                         headers=remember_headers)
