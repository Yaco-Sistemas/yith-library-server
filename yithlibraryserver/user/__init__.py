import bson
from pyramid.security import authenticated_userid


def get_authenticated_user(request):
    user_id = authenticated_userid(request)
    return request.db.users.find_one(bson.ObjectId(user_id))


def includeme(config):
    config.add_route('login', '/login')
    config.add_route('register_new_user', '/register')
    config.add_route('logout', '/logout')
