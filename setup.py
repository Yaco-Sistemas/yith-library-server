# Yith Library Server is a password storage server.
# Copyright (C) 2012-2013 Yaco Sistemas
# Copyright (C) 2012-2013 Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
# Copyright (C) 2012-2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of Yith Library Server.
#
# Yith Library Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yith Library Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Yith Library Server.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    # indirect dependencies
    'Beaker==1.6.4',            # required by pyramid_beaker
    'colander==1.0a2',          # required by deform
    'Chameleon==2.11',          # required by deform, pyramid
    'Mako==0.7.3',              # required by pyramid
    'MarkupSafe==0.15',         # required by Mako
    'nose==1.2.1',              # required by pymongo
    'PasteDeploy==1.5.0',       # required by pyramid
    'peppercorn==0.4',          # required by deform
    'Pygments==1.6',            # required by pyramid_debugtoolbar
    'repoze.lru==0.6',          # required by pyramid
    'repoze.sendmail==3.2',     # required by pyramid_mailer
    'transaction==1.4.1',       # required by pyramid_mailer
    'translationstring==1.1',   # required by deform, pyramid
    'venusian==1.0a8',          # required by pyramid
    'WebOb==1.2.3',             # required by pyramid
    'zope.deprecation==4.0.2',  # required by deform
    'zope.interface==4.0.5',    # required by pyramid

    # direct dependencies
    'deform==0.9.5',
    'pymongo==2.3',
    'pyramid==1.4',
    'pyramid_beaker==0.7',
    'pyramid_debugtoolbar==1.0.4',
    'pyramid_mailer==0.11',
    'pyramid_tm==0.7',
    'pyramid_sna==0.2',
    'raven==3.3.4',
    'requests==1.2.0',
    'waitress==2.1.1',
    ]

if sys.version_info[0] < 3:
    # Babel does not work with Python 3
    requires.append('Babel==0.9.6')

    requires.append('polib==1.0.3')  # required by lingua
    requires.append('xlwt==0.7.4')   # required by lingua
    requires.append('xlrd==0.9.0')   # required by lingua

    requires.append('lingua==1.4')

test_requires = [
    'WebTest==1.4.3',
    'mock==1.0.1',
    ]

docs_extras = [
    'docutils==0.10',  # required by Sphinx
    'Jinja2==2.6',     # required by Sphinx
    'Sphinx==1.1.3',
    ]

testing_extras = test_requires + [
    'nose==1.2.1',
    'coverage==3.6',
    ]


setup(name='yith-library-server',
      version='0.2',
      description='yith-library-server',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pyramid",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
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
      tests_require=requires + test_requires,
      extras_require = {
        'testing': testing_extras,
        'docs': docs_extras,
        },
      test_suite="yithlibraryserver",
      entry_points = """\
      [paste.app_factory]
      main = yithlibraryserver:main
      [console_scripts]
      yith_users_report = yithlibraryserver.scripts.reports:users
      yith_apps_report = yithlibraryserver.scripts.reports:applications
      yith_stats_report = yithlibraryserver.scripts.reports:statistics
      yith_migrate = yithlibraryserver.scripts.migrations:migrate
      yith_send_backups_via_email = yithlibraryserver.scripts.backups:send_backups_via_email
      yith_announce = yithlibraryserver.scripts.announce:announce""",
      message_extractors = {'.': [
            ('**.py', 'lingua_python', None),
            ('**.pt', 'lingua_xml', None),
        ]}
      )
