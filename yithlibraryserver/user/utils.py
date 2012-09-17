from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember


def split_name(name):
    parts = name.split(' ')
    if len(parts) > 1:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = parts[0]
        last_name = ''

    return first_name, last_name


def delete_user(db, user):
    result = db.users.remove(user['_id'], safe=True)
    return result['n'] == 1


def update_user(db, user, user_info):
    changes = {}
    for attribute in ('screen_name', 'first_name', 'last_name', 'email'):
        if attribute in user_info and user_info[attribute]:
            if attribute in user:
                if user_info[attribute] != user[attribute]:

                    changes[attribute] = user_info[attribute]
            else:
                changes[attribute] = user_info[attribute]

    if changes:
        db.users.update({'_id': user['_id']}, {'$set': changes},
                                safe=True)


def register_or_update(request, provider, user_id, info, default_url='/'):
    provider_key = '%s_id' % provider
    user = request.db.users.find_one({provider_key: user_id})
    if user is None:

        new_info = {'provider': provider, provider_key: user_id}
        for attribute in ('screen_name', 'first_name', 'last_name', 'email'):
            if attribute in info:
                new_info[attribute] = info[attribute]
            else:
                new_info[attribute] = ''

        request.session['user_info'] = new_info
        if 'next_url' not in request.session:
            request.session['next_url'] = default_url
        return HTTPFound(location=request.route_path('register_new_user'))
    else:
        update_user(request.db, user, info)
        if 'next_url' in request.session:
            next_url = request.session['next_url']
            del request.session['next_url']
        else:
            next_url = default_url

        request.session['current_provider'] = provider
        remember_headers = remember(request, str(user['_id']))
        return HTTPFound(location=next_url, headers=remember_headers)
