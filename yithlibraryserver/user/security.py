import bson

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound


def get_authenticated_user(request):
    user_id = authenticated_userid(request)
    try:
        user = request.db.users.find_one(bson.ObjectId(user_id))
    except bson.errors.InvalidId:
        raise HTTPFound(location=request.route_url('register_new_user'))
    else:
        return user
