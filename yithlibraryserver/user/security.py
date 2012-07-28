import bson

from pyramid.security import authenticated_userid, unauthenticated_userid
from pyramid.httpexceptions import HTTPFound


def get_user(request):
    user_id = unauthenticated_userid(request)
    if user_id is None:
        return user_id

    try:
        user = request.db.users.find_one(bson.ObjectId(user_id))
    except bson.errors.InvalidId:
        return None

    return user


def assert_authenticated_user_is_registered(request):
    user_id = authenticated_userid(request)
    try:
        user = request.db.users.find_one(bson.ObjectId(user_id))
    except bson.errors.InvalidId:
        raise HTTPFound(location=request.route_path('register_new_user'))
    else:
        return user
