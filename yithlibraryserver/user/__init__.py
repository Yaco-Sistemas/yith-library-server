def includeme(config):
    config.add_route('login', '/login')
    config.add_route('register_new_user', '/register')
    config.add_route('logout', '/logout')
    config.add_route('user_profile', '/profile')
    config.add_route('user_send_email_verification_code',
                     '/send-email-verification-code')
    config.add_route('user_verify_email', '/verify-email')
    config.add_route('user_merge_accounts', '/merge-accounts')
