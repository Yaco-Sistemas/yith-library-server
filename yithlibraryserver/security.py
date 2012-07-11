from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized


from yithlibraryserver.oauth2.authentication import find_access_code

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
