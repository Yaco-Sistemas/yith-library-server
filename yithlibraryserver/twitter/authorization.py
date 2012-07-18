import binascii
import hashlib
import hmac
import random
import time

from yithlibraryserver.compat import url_quote


def quote(value):
    return url_quote(value, safe='')


def nonce(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def timestamp():
    return int(time.time())


def sign(method, url, original_params, consumer_secret, oauth_token):
    # 1. create the parameter string
    param_string = '&'.join(['%s=%s' % (key, value) for key, value in sorted(original_params)])

    # 2. create signature base string
    signature_base = '%s&%s&%s' % (
        method.upper(), quote(url), quote(param_string),
        )

    # 3. create the signature key
    key = '%s&%s' % (quote(consumer_secret), quote(oauth_token))

    # 4. calculate the signature
    hashed = hmac.new(key.encode('ascii'),
                      signature_base.encode('ascii'),
                      hashlib.sha1)
    return quote(binascii.b2a_base64(hashed.digest())[:-1])


def auth_header(method, url, original_params, settings, oauth_token='', nonce_=None, timestamp_=None):
    params = list(original_params) + [
        ('oauth_consumer_key', settings['twitter.consumer_key']),
        ('oauth_nonce', nonce_ or nonce()),
        ('oauth_signature_method', 'HMAC-SHA1'),
        ('oauth_timestamp', str(timestamp_ or timestamp())),
        ('oauth_version', '1.0'),
        ]
    params = [(quote(key), quote(value)) for key, value in params]

    signature = sign(method, url, params,
                     settings['twitter.consumer_secret'], oauth_token)
    params.append(('oauth_signature', signature))

    header = ", ".join(['%s="%s"' % (key, value) for key, value in params])

    return 'OAuth %s' % header
