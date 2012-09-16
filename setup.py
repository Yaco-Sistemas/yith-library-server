import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'deform==0.9.5',
    'pymongo==2.3',
    'pyramid==1.3.4',
    'pyramid_beaker==0.7',
    'pyramid_debugtoolbar==1.0.2',
    'pyramid_mailer==0.9',
    'pyramid_tm==0.5',
    'python-openid==2.2.5',
    'requests==0.14.0',
    'waitress==0.8.1',
    ]

setup(name='yith-library-server',
      version='0.0',
      description='yith-library-server',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + ['webtest', 'mock', 'nose', 'coverage'],
      test_suite="yithlibraryserver",
      entry_points = """\
      [paste.app_factory]
      main = yithlibraryserver:main
      [console_scripts]
      migrate_set_unverified_emails = yithlibraryserver.scripts.migrate:set_unverified_emails
      """,
      )

