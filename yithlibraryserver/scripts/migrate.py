import optparse
import textwrap
import sys

from pyramid.paster import bootstrap

def set_unverified_emails():
    description = "Update the users to have unverified emails."
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']

    try:
        db = settings['mongodb'].get_database()
        for user in db.users.find():
            print '%s %s' % (user.get('first_name', ''),
                             user.get('last_name', ''))

    finally:
        closer()


if __name__ == '__main__':
    set_unverified_emails()
