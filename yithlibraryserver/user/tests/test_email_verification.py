from pyramid import testing
from pyramid.testing import DummyRequest
from pyramid.request import Request

from pyramid_mailer import get_mailer

from yithlibraryserver.testing import TestCase
from yithlibraryserver.user.email_verification import EmailVerificationCode

class EmailVerificationCodeTests(TestCase):

    clean_collections = ('users', )
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        super(EmailVerificationCodeTests, self).setUp()

    def test_email_verification_code(self):
        evc = EmailVerificationCode()

        self.assertNotEqual(evc.code, None)

        user_id = self.db.users.insert({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                }, safe=True)
        user = self.db.users.find_one({'_id': user_id})
        evc.store(self.db, user)

        user = self.db.users.find_one({'_id': user_id})
        self.assertEqual(user['email_verification_code'], evc.code)

        evc2 = EmailVerificationCode(evc.code)
        result = evc2.verify(self.db, 'john@example.com')
        self.assertTrue(result)

        evc2.remove(self.db, 'john@example.com', True)
        user = self.db.users.find_one({'_id': user_id})
        self.assertFalse('email_verification_code' in user)
        self.assertTrue(user['email_verified'])

        request = DummyRequest()
        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 0)
        evc2.send(request, user, 'http://example.com/verify')

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject,
                         'Please verify your email address')
        self.assertEqual(mailer.outbox[0].recipients,
                         ['john@example.com'])
