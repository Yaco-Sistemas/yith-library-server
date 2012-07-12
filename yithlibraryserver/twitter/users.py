def get_user(request, user_id):
    return request.db.users.find_one({'provider_user_id': user_id})
