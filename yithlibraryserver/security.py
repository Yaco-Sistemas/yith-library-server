from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized
from pyramid.security import Allow, Authenticated


from yithlibraryserver.oauth2.authorization import AccessCodes


class RootFactory(object):

    __acl__ = (
        (Allow, Authenticated, 'user-registration'),
        (Allow, Authenticated, 'view-applications'),
        (Allow, Authenticated, 'edit-application'),
        (Allow, Authenticated, 'add-application'),
        (Allow, Authenticated, 'delete-application'),
        (Allow, Authenticated, 'add-authorized-app'),
        (Allow, Authenticated, 'revoke-authorized-app'),
        )

    def __init__(self, request):
        self.request = request


def authorize_user(request):
    authorization = request.headers.get('Authorization')
    if authorization is None:
        raise HTTPUnauthorized()

    method, credentials = request.authorization
    if method.lower() != 'bearer':
        raise HTTPBadRequest('Authorization method not supported')

    access_code = AccessCodes(request.db).find(credentials)
    if access_code is None:
        raise HTTPUnauthorized()

    user_id = access_code['user']
    user = request.db.users.find_one(user_id)
    if user is None:
        raise HTTPUnauthorized()

    return user
