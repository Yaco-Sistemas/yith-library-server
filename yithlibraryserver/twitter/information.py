import requests

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.compat import url_encode
from yithlibraryserver.twitter.authorization import auth_header


def get_user_info(settings, user_id, oauth_token):
    user_info_url = settings['twitter_user_info_url']

    params = (
        ('oauth_token', oauth_token),
        )

    auth = auth_header('GET', user_info_url, params, settings, oauth_token)

    response = requests.get(
        user_info_url + '?' + url_encode({'user_id': user_id}),
        headers={'Authorization': auth},
        )

    if response.status_code != 200:
        raise HTTPUnauthorized(response.text)

    return response.json
