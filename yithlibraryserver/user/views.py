from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, remember, forget
from pyramid.view import view_config, forbidden_view_config

from yithlibraryserver.compat import url_quote

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = request.route_url('home')
    came_from = request.params.get('came_from', referrer)
    return {'next_url': url_quote(came_from)}


@view_config(route_name='register_new_user',
             renderer='templates/register.pt',
             permission='user-registration')
def register_new_user(request):
    if 'submit' in request.POST:
        user_id = authenticated_userid(request)
        screen_name = request.POST['screen_name']
        next_url = request.POST['next_url']

        _id = request.db.users.insert({
                'provider_user_id': user_id,
                'screen_name': screen_name,
                'authorized_apps': [],
                }, safe=True)
        return HTTPFound(location=next_url,
                         headers=remember(request, str(_id)))

    return {
        'user_id': authenticated_userid(request),
        'screen_name': request.params.get('screen_name', ''),
        'next_url': request.params.get('next_url', request.route_url('home')),
        }


@view_config(route_name='logout', renderer='string')
def logout(request):
    return HTTPFound(location=request.route_url('home'),
                     headers=forget(request))
