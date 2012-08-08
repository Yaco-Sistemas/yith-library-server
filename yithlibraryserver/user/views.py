from deform import Button, Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config, forbidden_view_config

from yithlibraryserver.compat import url_quote
from yithlibraryserver.user.schemas import UserSchema


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_path('login')
    referrer = request.path
    if request.query_string:
        referrer += '?' + request.query_string
    if referrer == login_url:
        referrer = request.route_path('home')
    came_from = request.params.get('came_from', referrer)
    return {'next_url': url_quote(came_from)}


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
        next_url = request.route_url('home')

    schema = UserSchema()
    button1 = Button('submit', 'Register into Yith Library')
    button1.css_class = 'btn-primary'
    button2 = Button('cancel', 'Cancel')
    button2.css_class = ''

    form = Form(schema, buttons=(button1, button2))

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        provider = user_info['provider']
        provider_key = provider + '_id'

        _id = request.db.users.insert({
                provider_key: user_info[provider_key],
                'screen_name': user_info.get('screen_name', ''),
                'first_name': appstruct['first_name'],
                'last_name': appstruct['last_name'],
                'email': appstruct['email'],
                'authorized_apps': [],
                }, safe=True)

        del request.session['user_info']
        if 'next_url' in request.session:
            del request.session['next_url']

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
                'email': user_info.get('email', ''),
                }),
        }


@view_config(route_name='logout', renderer='string')
def logout(request):
    return HTTPFound(location=request.route_path('home'),
                     headers=forget(request))
