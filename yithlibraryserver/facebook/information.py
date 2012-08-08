import requests

from pyramid.httpexceptions import HTTPUnauthorized

from yithlibraryserver.compat import url_encode


def get_user_info(settings, access_token):
    basic_information_url = '%s?%s' % (
        settings['facebook_basic_information_url'],
        url_encode({'access_token': access_token}),
        )
    response = requests.get(basic_information_url)

    if response.status_code != 200:
        raise HTTPUnauthorized(response.text)

    return response.json
