# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012-2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of Yith Library Server.
#
# Yith Library Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yith Library Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.
import datetime

from deform import Button, Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.i18n import get_localizer
from pyramid.security import remember, forget
from pyramid.view import view_config, view_defaults, forbidden_view_config

from yithlibraryserver.compat import url_quote
from yithlibraryserver.i18n import translation_domain
from yithlibraryserver.i18n import TranslationString as _
from yithlibraryserver.user import analytics
from yithlibraryserver.user.accounts import get_accounts, merge_accounts
from yithlibraryserver.user.accounts import notify_admins_of_account_removal
from yithlibraryserver.user.email_verification import EmailVerificationCode
from yithlibraryserver.user.schemas import UserSchema, NewUserSchema
from yithlibraryserver.user.schemas import AccountDestroySchema
from yithlibraryserver.user.schemas import UserPreferencesSchema
from yithlibraryserver.user.utils import delete_user
from yithlibraryserver.password.models import PasswordsManager
from yithlibraryserver.security import authorize_user


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_path('login')
    referrer = request.path
    if request.query_string:
        referrer += '?' + request.query_string
    if referrer == login_url:
        referrer = request.route_path('oauth2_clients')
    came_from = request.params.get('came_from', referrer)
    return {
        'identity_providers': request.registry.identity_providers,
        'next_url': url_quote(came_from),
        }


@view_config(route_name='register_new_user',
             renderer='templates/register.pt')
def register_new_user(request):
    try:
        user_info = request.session['user_info']
    except KeyError:
        return HTTPBadRequest('Missing user info in the session')

    try:
        next_url = request.session['next_url']
    except KeyError:
        next_url = request.route_url('oauth2_clients')

    schema = NewUserSchema()
    button1 = Button('submit', _('Register into Yith Library'))
    button1.css_class = 'btn-primary'
    button2 = Button('cancel', _('Cancel'))
    button2.css_class = ''

    form = Form(schema, buttons=(button1, button2))

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {
                'form': e.render(),
                'provider': user_info.get('provider', ''),
                'email': user_info.get('email', ''),
                'next_url': next_url,
                }

        provider = user_info['provider']
        provider_key = provider + '_id'

        if (appstruct['email'] != ''
            and appstruct['email'] == user_info['email']):
            email_verified = True
        else:
            email_verified = False

        now = datetime.datetime.utcnow()

        user_attrs = {
                provider_key: user_info[provider_key],
                'screen_name': appstruct['screen_name'],
                'first_name': appstruct['first_name'],
                'last_name': appstruct['last_name'],
                'email': appstruct['email'],
                'email_verified': email_verified,
                'authorized_apps': [],
                'date_joined': now,
                'last_login': now,
            }

        if request.google_analytics.is_in_session():
            allow_analytics = request.google_analytics.show_in_session()
            user_attrs[analytics.USER_ATTR] = allow_analytics
            request.google_analytics.clean_session()

        _id = request.db.users.insert(user_attrs, safe=True)

        if not email_verified and appstruct['email'] != '':
            evc = EmailVerificationCode()
            user = request.db.users.find_one({'_id': _id})
            if evc.store(request.db, user):
                link = request.route_url('user_verify_email')
                evc.send(request, user, link)

        del request.session['user_info']
        if 'next_url' in request.session:
            del request.session['next_url']

        request.session['current_provider'] = provider
        return HTTPFound(location=next_url,
                         headers=remember(request, str(_id)))
    elif 'cancel' in request.POST:
        del request.session['user_info']
        if 'next_url' in request.session:
            del request.session['next_url']

        return HTTPFound(location=next_url)

    return {
        'form': form.render({
                'first_name': user_info.get('first_name', ''),
                'last_name': user_info.get('last_name', ''),
                'screen_name': user_info.get('screen_name', ''),
                'email': user_info.get('email', ''),
                }),
        'provider': user_info.get('provider', ''),
        'email': user_info.get('email', ''),
        'next_url': next_url,
        }


@view_config(route_name='logout', renderer='string')
def logout(request):
    if 'current_provider' in request.session:
        del request.session['current_provider']

    return HTTPFound(location=request.route_path('home'),
                     headers=forget(request))


@view_config(route_name='user_destroy',
             renderer='templates/destroy.pt',
             permission='destroy-account')
def destroy(request):
    schema = AccountDestroySchema()
    button1 = Button('submit', _('Yes, I am sure. Destroy my account'))
    button1.css_class = 'btn-danger'
    button2 = Button('cancel', _('Cancel'))
    button2.css_class = ''

    form = Form(schema, buttons=(button1, button2))

    passwords_manager = PasswordsManager(request.db)
    context = {
        'passwords': passwords_manager.retrieve(request.user).count(),
        }

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            context['form'] = e.render()
            return context

        reason = appstruct['reason']
        admin_emails = request.registry.settings['admin_emails']
        if admin_emails:
            notify_admins_of_account_removal(request, request.user,
                                             reason, admin_emails)

        passwords_manager.delete(request.user)
        # TODO: remove user's applications
        delete_user(request.db, request.user)

        request.session.flash(
            _('Your account has been removed. Have a nice day!'),
            'success',
            )
        return logout(request)

    elif 'cancel' in request.POST:
        request.session.flash(
            _('Thanks for reconsidering removing your account!'),
            'info',
            )
        return HTTPFound(location=request.route_path('user_information'))

    context['form'] = form.render()
    return context


@view_config(route_name='user_information',
             renderer='templates/user_information.pt',
             permission='edit-profile')
def user_information(request):
    schema = UserSchema()
    button1 = Button('submit', _('Save changes'))
    button1.css_class = 'btn-primary'

    form = Form(schema, buttons=(button1, ))

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        changes = {
            'first_name': appstruct['first_name'],
            'last_name': appstruct['last_name'],
            'screen_name': appstruct['screen_name'],
            'email': appstruct['email']['email'],
            }

        if request.user['email'] != appstruct['email']['email']:
            changes['email_verified'] = False

        result = request.db.users.update({'_id': request.user['_id']},
                                         {'$set': changes},
                                         safe=True)

        if result['n'] == 1:
            request.session.flash(
                _('The changes were saved successfully'),
                'success',
                )
            return HTTPFound(location=request.route_path('user_information'))
        else:
            request.session.flash(
                _('There were an error while saving your changes'),
                'error',
                )
            return {'form': appstruct}

    return {
        'form': form.render({
                'first_name': request.user['first_name'],
                'last_name': request.user['last_name'],
                'screen_name': request.user['screen_name'],
                'email': {
                    'email': request.user['email'],
                    'email_verified': request.user['email_verified'],
                    },
                }),
        }


@view_config(route_name='user_preferences',
             renderer='templates/preferences.pt',
             permission='edit-profile')
def preferences(request):
    schema = UserPreferencesSchema()
    button1 = Button('submit', _('Save changes'))
    button1.css_class = 'btn-primary'

    form = Form(schema, buttons=(button1, ))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        changes = {
            analytics.USER_ATTR: appstruct[analytics.USER_ATTR],
            }

        result = request.db.users.update({'_id': request.user['_id']},
                                         {'$set': changes},
                                         safe=True)

        if result['n'] == 1:
            request.session.flash(
                _('The changes were saved successfully'),
                'success',
                )
            return HTTPFound(location=request.route_path('user_preferences'))
        else:
            request.session.flash(
                _('There were an error while saving your changes'),
                'error',
                )
            return {'form': appstruct}

    return {'form': form.render(request.user)}


@view_config(route_name='user_identity_providers',
             renderer='templates/identity_providers.pt',
             permission='edit-profile')
def identity_providers(request):
    current_provider = request.session.get('current_provider', None)
    accounts = get_accounts(request.db, request.user, current_provider)
    context = {
        'accounts': accounts
    }
    verified = [ac for ac in accounts if ac['is_verified']]
    context['can_merge'] = len(verified) > 1

    if 'submit' in request.POST:
        if not context['can_merge']:
            return HTTPBadRequest('You do not have enough accounts to merge')

        def is_verified(ac):
            for a in accounts:
                if a['id'] == ac:
                    return a['is_verified']
            return False

        accounts_to_merge = [account.replace('account-', '')
                             for account in request.POST.keys()
                             if account != 'submit']
        accounts_to_merge = [account
                             for account in accounts_to_merge
                             if is_verified(account)]

        if len(accounts_to_merge) > 1:
            merged = merge_accounts(request.db, request.user,
                                    accounts_to_merge)
            localizer = get_localizer(request)
            msg = localizer.pluralize(
                _('Congratulations, ${n_merged} of your accounts has been merged into the current one'),
                _('Congratulations, ${n_merged} of your accounts have been merged into the current one'),
                merged,
                domain=translation_domain,
                mapping={'n_merged': merged},
                )
            request.session.flash(msg, 'success')
        else:
            request.session.flash(
                _('Not enough accounts for merging'),
                'error',
                )

        return HTTPFound(
            location=request.route_path('user_identity_providers'))

    return context


@view_config(route_name='user_send_email_verification_code',
             renderer='json',
             permission='edit-profile')
def send_email_verification_code(request):
    if not request.user['email']:
        return {
            'status': 'bad',
            'error': 'You have not an email in your profile',
            }

    if 'submit' in request.POST:
        evc = EmailVerificationCode()
        if evc.store(request.db, request.user):
            link = request.route_url('user_verify_email')
            evc.send(request, request.user, link)
            return {'status': 'ok', 'error': None}
        else:
            return {
                'status': 'bad',
                'error': 'There were problems storing the verification code',
                }
    else:
        return {'status': 'bad', 'error': 'Not a post'}


@view_config(route_name='user_verify_email',
             renderer='templates/verify_email.pt')
def verify_email(request):
    try:
        code = request.params['code']
    except KeyError:
        return HTTPBadRequest('Missing code parameter')

    try:
        email = request.params['email']
    except KeyError:
        return HTTPBadRequest('Missing email parameter')

    evc = EmailVerificationCode(code)
    if evc.verify(request.db, email):
        request.session.flash(
            _('Congratulations, your email has been successfully verified'),
            'success',
            )
        evc.remove(request.db, email, True)
        return {
            'verified': True,
            }
    else:
        request.session.flash(
            _('Sorry, your verification code is not correct or has expired'),
            'error',
            )
        return {
            'verified': False,
            }


@view_config(route_name='user_google_analytics_preference', renderer='json')
def google_analytics_preference(request):
    if 'yes' in request.POST:
        allow = True
    elif 'no' in request.POST:
        allow = False
    else:
        return HTTPBadRequest('Missing preference parameter')

    if request.user is None:
        request.session[analytics.USER_ATTR] = allow
    else:
        changes = request.google_analytics.get_user_attr(allow)
        request.db.users.update({'_id': request.user['_id']},
                                {'$set': changes},
                                safe=True)

    return {'allow': allow}


@view_defaults(route_name='user_view', renderer='json')
class UserRESTView(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='OPTIONS', renderer='string')
    def options(self):
        headers = self.request.response.headers
        headers['Access-Control-Allow-Methods'] = 'GET'
        headers['Access-Control-Allow-Headers'] = ('Origin, Content-Type, '
                                                   'Accept, Authorization')
        return ''

    @view_config(request_method='GET')
    def get(self):
        return authorize_user(self.request)
