def split_name(name):
    parts = name.split(' ')
    if len(parts) > 1:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = parts[0]
        last_name = ''

    return first_name, last_name


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
