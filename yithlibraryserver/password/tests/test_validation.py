import unittest

from yithlibraryserver.password.validation import validate_password


class UtilsTests(unittest.TestCase):

    def test_validate_password(self):
        # empty json
        password, errors = validate_password(b'')
        self.assertEqual(password, {})
        self.assertEqual(errors, ['No JSON object could be decoded'])

        # bad json
        password, errors = validate_password(b'[1')
        self.assertEqual(password, {})
        self.assertEqual(errors, ['No JSON object could be decoded'])

        # id not in the URL
        password, errors = validate_password(b'{}', _id='1')
        self.assertEqual(errors, ['The password id must be in the body',
                                  'Secret is required',
                                  'Service is required'])

        # id doesn't match URL's id
        password, errors = validate_password(b'{"_id": "1"}', _id='2')
        self.assertEqual(errors, ['The password id does not match the URL',
                                  'Secret is required',
                                  'Service is required'])

        # secret is missing
        password, errors = validate_password(b'{"_id": "1"}', _id='1')
        self.assertEqual(errors, ['Secret is required',
                                  'Service is required'])

        # service is missing
        password, errors = validate_password(b'{"_id": "1", "secret": "s3cr3t"}', _id='1')
        self.assertEqual(errors, ['Service is required'])

        # everything is fine
        password, errors = validate_password(b'{"_id": "1", "secret": "s3cr3t", "service": "myservice"}', _id='1')
        self.assertEqual(errors, [])
        self.assertEqual(password, {
                '_id': '1',
                'secret': 's3cr3t',
                'service': 'myservice',
                'account': None,
                'expiration': None,
                'notes': None,
                'tags': None,
                'creation': None,
                'last_modification': None,
                })
