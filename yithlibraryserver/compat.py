import sys
import types

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3: # pragma: no cover
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    long = int
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    long = long

if PY3: # pragma: no cover
    from urllib import parse
    urlparse = parse
    from urllib.parse import quote as url_quote
    from urllib.parse import urlencode as url_encode
else:
    import urlparse
    from urllib import quote as url_quote
    from urllib import urlencode as url_encode

if PY3:
    from base64 import decodebytes, encodebytes
else:
    from base64 import decodestring as decodebytes
    from base64 import encodestring as encodebytes
