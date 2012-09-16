import bson

from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


def get_available_providers():
    return ('facebook', 'google', 'twitter')


def get_providers(user):
    result = []
    for provider in get_available_providers():
        key = provider + '_id'
        if key in user and user[key] is not None:
            result.append(provider)
    return result


def get_n_passwords(db, user):
    return db.passwords.find({'owner': user['_id']}, safe=True).count()


def get_accounts(db, user):
    email = user.get('email', None)
    results = db.users.find({'email_verified': True, 'email': email},
                            safe=True)
    return [{'providers': get_providers(user),
             'passwords': get_n_passwords(db, user),
             'id': str(user['_id'])}
            for user in results]


def merge_accounts(db, master_user, accounts):
    merged = 0

    for account in accounts:
        user_id = bson.ObjectId(account)
        if master_user['_id'] == user_id:
            continue

        current_user = db.users.find_one({'_id': user_id}, safe=True)
        if current_user is None:
            continue

        merge_users(db, master_user, current_user)

        merged += 1

    return merged


def merge_users(db, user1, user2):
    # move all passwords of user2 to user1
    db.passwords.update({'owner': user2['_id']}, {
            '$set': {
                'owner': user1['_id'],
                },
            }, multi=True, safe=True)

    # copy authorized_apps from user2 to user1
    updates = {
        '$addToSet': {
            'authorized_apps': {
                '$each': user2['authorized_apps'],
                },
            },
        }

    # copy the providers
    for provider in get_available_providers():
        key = provider + '_id'
        if key in user2 and key not in user1:
            sets = updates.setdefault('$set', {})
            sets[key] = user2[key]

    db.users.update({'_id': user1['_id']}, updates, safe=True)

    # remove user2
    db.users.remove(user2['_id'])


def notify_admins_of_account_removal(request, user, reason):
    settings = request.registry.settings
    admin_emails = settings['admin_emails']

    if not admin_emails:
        return

    home_link = request.route_url('home')
    reason = reason or 'no reason was given'

    text_body = render(
        'yithlibraryserver.user:templates/account_removal_notification.txt',
        {'reason': reason, 'user': user, 'home_link': home_link},
        request=request,
        )
    # chamaleon txt templates are rendered as utf-8 bytestrings
    text_body = unicode(text_body, 'utf-8')

    html_body = render(
        'yithlibraryserver.user:templates/account_removal_notification.pt',
        {'reason': reason, 'user': user, 'home_link': home_link},
        request=request,
        )

    message = Message(subject='A user has destroyed his Yith Library account',
                      recipients=admin_emails,
                      body=text_body,
                      html=html_body)
    get_mailer(request).send(message)
