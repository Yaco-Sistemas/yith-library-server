from pyramid.httpexceptions import HTTPFound

from openid.consumer import consumer
from openid.extensions import ax
from openid.store.filestore import FileOpenIDStore

from yithlibraryserver.compat import urlparse
from yithlibraryserver.user.utils import register_or_update

def _get_consumer(request):
    settings = request.registry.settings
    store = FileOpenIDStore(settings['google_openid_store_path'])
    return consumer.Consumer(request.session, store)


def _get_google_id(url):
    parts = urlparse.urlparse(url)
    query = dict(urlparse.parse_qsl(parts.query))
    return query['id']


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
        user_id = _get_google_id(info.getDisplayIdentifier())
        info = {
                'provider': 'google',
                'google_id': user_id,
                'first_name': fr.getSingle(AX_ATTRS['first_name']),
                'last_name': fr.getSingle(AX_ATTRS['last_name']),
                'email': fr.getSingle(AX_ATTRS['email']),
            }
        return register_or_update(request, 'google', user_id, info,
                                  default_url=request.route_path('home'))

    elif info.status == consumer.CANCEL:
        return 'canceled'
    elif info.status == consumer.FAILURE:
        return 'failure'
    elif info.status == consumer.SETUP_NEEDED:
        return 'setup needed'
    else:
        return 'unknown failure'
