0.2 (2013-02-03)
----------------
- New features:

  - Import/export of password collections
  - Periodic mailing of password backup files
  - New report to get statistics of usage
  - Rename old usage report to users since it just list the users
  - Improve gravatar icon style in the header
  - Make Persona logout more robust
  - Improve the marketing (Twitter and Github links)

- Regressions:

  - Remove Python 3 support because of a pyramid_mailer's bug. The bug (#24)
    has been fixed but no new release has been made as of this writing.

0.1 (2013-01-13)
----------------
- Oauth2 protocol to access the passwords with a RESTful API
- Facebook, Google, Mozilla Persona and Twitter authentication methods
- Account merging to allow several authentication methods for one account
- User profile with Gravatar integration
- Account removal
- Localized to English and Spanish languages
- Google Analytics support that users can avoid
- 100% test coverage
- Landing, terms of service and contact pages
