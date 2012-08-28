from pyramid.httpexceptions import HTTPFound

from openid.consumer import consumer
from openid.extensions import ax
from openid.store.filestore import FileOpenIDStore

from yithlibraryserver.compat import urlparse

def _get_consumer(request):
    settings = request.registry.settings
    store = FileOpenIDStore(settings['google_openid_store_path'])
    return consumer.Consumer(request.session, store)


AX_ATTRS = {
    'firstname': 'http://axschema.org/namePerson/first',
    'lastname': 'http://axschema.org/namePerson/last',
    'email': 'http://axschema.org/contact/email',
}


def google_login(request):
    settings = request.registry.settings
    openid_url = settings['google_openid_url']

    consumer = _get_consumer(request)
    auth_req = consumer.begin(openid_url)

    fetch_req = ax.FetchRequest()
    fetch_req.add(ax.AttrInfo(AX_ATTRS['firstname'], required=True))
    fetch_req.add(ax.AttrInfo(AX_ATTRS['lastname'], required=True))
    fetch_req.add(ax.AttrInfo(AX_ATTRS['email'], required=True))

    auth_req.addExtension(fetch_req)

    return_to = request.route_url('google_callback')
    parts = urlparse.urlparse(return_to)
    realm = '%s://%s/' % (parts.scheme, parts.netloc)

    return HTTPFound(location=auth_req.redirectURL(realm, return_to=return_to))


def google_callback(request):
    con = _get_consumer(request)
    info = con.complete(request.GET, request.url)
    if info.status == consumer.SUCCESS:
        fr = ax.FetchResponse.fromSuccessResponse(info)
        print fr.getSingle(AX_ATTRS['firstname'])
        print fr.getSingle(AX_ATTRS['lastname'])
        print fr.getSingle(AX_ATTRS['email'])
        return info.getDisplayIdentifier()
    elif info.status == consumer.CANCEL:
        return 'canceled'
    elif info.status == consumer.FAILURE:
        return 'failure'
    elif info.status == consumer.SETUP_NEEDED:
        return 'setup needed'
    else:
        return 'unknown failure'
