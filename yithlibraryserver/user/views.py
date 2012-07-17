from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, remember, forget
from pyramid.view import view_config, forbidden_view_config


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    return {}


@view_config(route_name='register_new_user',
             renderer='templates/register.pt',
             permission='user-registration')
def register_new_user(request):
    if 'submit' in request.POST:
        user_id = authenticated_userid(request)
        screen_name = request.POST['screen_name']

        _id = request.db.users.insert({
                'provider_user_id': user_id,
                'screen_name': screen_name,
                'authorized_apps': [],
                }, safe=True)
        next_url = request.route_url('oauth2_applications')
        return HTTPFound(location=next_url,
                         headers=remember(request, str(_id)))

    return {
        'user_id': authenticated_userid(request),
        'screen_name': request.params.get('screen_name', '')
        }


@view_config(route_name='logout', renderer='string')
def logout(request):
    return HTTPFound(location=request.route_url('login'),
                     headers=forget(request))
