from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized
from pyramid.security import Allow, Authenticated


from yithlibraryserver.oauth2.authentication import find_access_code


class RootFactory(object):

    __acl__ = (
        (Allow, Authenticated, 'user-registration'),
        (Allow, Authenticated, 'view-applications'),
        (Allow, Authenticated, 'view-application'),
        (Allow, Authenticated, 'add-application'),
        (Allow, Authenticated, 'delete-application'),
        (Allow, Authenticated, 'add-authorized-app'),
        )

    def __init__(self, request):
        self.request = request


def authorize_user(request, user):
    authorization = request.headers.get('Authorization')
    if authorization is None:
        raise HTTPUnauthorized()

    method, credentials = request.authorization
    if method.lower() != 'bearer':
        raise HTTPBadRequest('Authorization method not supported')

    access_code = find_access_code(request, credentials)
    if access_code is None:
        raise HTTPUnauthorized()

    if access_code['user'] != user:
        raise HTTPUnauthorized()
