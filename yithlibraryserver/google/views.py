from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember

from openid.consumer import consumer
from openid.extensions import ax
from openid.store.filestore import FileOpenIDStore

from yithlibraryserver.compat import urlparse
from yithlibraryserver.user.utils import update_user

def _get_consumer(request):
    settings = request.registry.settings
    store = FileOpenIDStore(settings['google_openid_store_path'])
    return consumer.Consumer(request.session, store)


AX_ATTRS = {
    'first_name': 'http://axschema.org/namePerson/first',
    'last_name': 'http://axschema.org/namePerson/last',
    'email': 'http://axschema.org/contact/email',
}


def google_login(request):
    settings = request.registry.settings
    openid_url = settings['google_openid_url']

    consumer = _get_consumer(request)
    auth_req = consumer.begin(openid_url)

    fetch_req = ax.FetchRequest()
    fetch_req.add(ax.AttrInfo(AX_ATTRS['first_name'], required=True))
    fetch_req.add(ax.AttrInfo(AX_ATTRS['last_name'], required=True))
    fetch_req.add(ax.AttrInfo(AX_ATTRS['email'], required=True))

    auth_req.addExtension(fetch_req)

    return_to = request.route_url('google_callback')
    parts = urlparse.urlparse(return_to)
    realm = '%s://%s/' % (parts.scheme, parts.netloc)

    if 'next_url' in request.params:
        request.session['next_url'] = request.params['next_url']

    return HTTPFound(location=auth_req.redirectURL(realm, return_to=return_to))


def google_callback(request):
    con = _get_consumer(request)
    info = con.complete(request.GET, request.url)
    if info.status == consumer.SUCCESS:
        fr = ax.FetchResponse.fromSuccessResponse(info)
        user_id = info.getDisplayIdentifier()

        if 'next_url' in request.session:
            next_url = request.session['next_url']
            del request.session['next_url']
        else:
            next_url = request.route_path('home')

        user = request.db.users.find_one({'google_id': user_id})
        info = {
                'provider': 'google',
                'google_id': user_id,
                'first_name': fr.getSingle(AX_ATTRS['first_name']),
                'last_name': fr.getSingle(AX_ATTRS['last_name']),
                'email': fr.getSingle(AX_ATTRS['email']),
            }
        if user is None:
            request.session['user_info'] = info
            request.session['next_url'] = next_url
            return HTTPFound(location=request.route_path('register_new_user'))
        else:
            update_user(request.db, user, info)
            remember_headers = remember(request, str(user['_id']))
            return HTTPFound(location=next_url, headers=remember_headers)

    elif info.status == consumer.CANCEL:
        return 'canceled'
    elif info.status == consumer.FAILURE:
        return 'failure'
    elif info.status == consumer.SETUP_NEEDED:
        return 'setup needed'
    else:
        return 'unknown failure'
