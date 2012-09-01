from mock import patch

from openid.association import Association
from openid.consumer.consumer import AuthRequest
from openid.consumer.discover import OpenIDServiceEndpoint

from yithlibraryserver import testing
from yithlibraryserver.compat import urlparse


XRDS = '<?xml version="1.0" encoding="UTF-8"?>\n<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">\n<XRD>\n<Service priority="0">\n<Type>http://specs.openid.net/auth/2.0/server</Type>\n<Type>http://openid.net/srv/ax/1.0</Type>\n<Type>http://specs.openid.net/extensions/ui/1.0/mode/popup</Type>\n<Type>http://specs.openid.net/extensions/ui/1.0/icon</Type>\n<Type>http://specs.openid.net/extensions/pape/1.0</Type>\n<URI>https://www.google.com/accounts/o8/ud</URI>\n</Service>\n</XRD>\n</xrds:XRDS>\n'

ASSOC_HANDLE = 'AMlYA9W_FbThybIcK6l0Wdl95D11KtOA3zDpTU8juWzgKMY-xlqf3bh0'


def get_association():
    secret = '\xe1\xee\xae>n|\xaa*="Elq\x1c"n\xe4u3\xbf'
    issued = 1346478836
    lifetime = 46799
    assoc_type = 'HMAC-SHA1'
    return Association(ASSOC_HANDLE, secret, issued, lifetime, assoc_type)


class ViewTests(testing.TestCase):

    clean_collections = ('users', )

    def test_google_login(self):
        with patch('openid.consumer.consumer.Consumer.begin') as fake:
            # we don't want to hit the wire in the tests
            # so we avoid the discovery and association handle
            # steps with this code
            endpoints = OpenIDServiceEndpoint.fromXRDS(
                'https://www.google.com/accounts/o8/ud',
                XRDS,
                )
            association = get_association()
            auth_req = AuthRequest(endpoints[0], association)
            auth_req.setAnonymous(False)
            fake.return_value = auth_req

            res = self.testapp.get('/google/login', {
                    'next_url': 'https://localhost/foo/bar',
                    })
            self.assertEqual(res.status, '302 Found')
            url = urlparse.urlparse(res.location)
            self.assertEqual(url.netloc, 'www.google.com')
            self.assertEqual(url.path, '/accounts/o8/ud')
            query = urlparse.parse_qs(url.query)
            self.assertEqual(tuple(query.keys()),
                             ('openid.ns', 'openid.realm', 'openid.return_to',
                              'openid.ax.mode', 'openid.claimed_id', 'openid.mode',
                              'openid.ns.ax', 'openid.identity', 'openid.assoc_handle',
                              'openid.ax.required', 'openid.ax.type.ext0', 'openid.ax.type.ext1', 'openid.ax.type.ext2'))
            self.assertEqual(query['openid.ns'],
                             ['http://specs.openid.net/auth/2.0'])
            self.assertEqual(query['openid.realm'],
                             ['http://localhost/'])
            self.assertEqual(query['openid.return_to'],
                             ['http://localhost/google/callback'])
            self.assertEqual(query['openid.ax.mode'], ['fetch_request'])
            self.assertEqual(query['openid.claimed_id'],
                             ['http://specs.openid.net/auth/2.0/identifier_select'])
            self.assertEqual(query['openid.mode'], ['checkid_setup'])
            self.assertEqual(query['openid.ns.ax'],
                             ['http://openid.net/srv/ax/1.0'])
            self.assertEqual(query['openid.identity'],
                             ['http://specs.openid.net/auth/2.0/identifier_select'])
            self.assertEqual(query['openid.assoc_handle'], [ASSOC_HANDLE])
            self.assertEqual(query['openid.ax.required'], ['ext0,ext1,ext2'])
            self.assertEqual(query['openid.ax.type.ext0'],
                             ['http://axschema.org/namePerson/first'])
            self.assertEqual(query['openid.ax.type.ext1'],
                             ['http://axschema.org/namePerson/last'])
            self.assertEqual(query['openid.ax.type.ext2'],
                             ['http://axschema.org/contact/email'])
