from __future__ import print_function

import os
import sys
from setuptools import setup, find_packages


PY3 = sys.version_info[0] > 2

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pyramid>=1.4.5',
    'SQLAlchemy>=0.8.2',
    'alembic>=0.6.7',
    'transaction>=1.4.3',
    'pyramid_tm>=0.7',
    'pyramid_debugtoolbar>=2.2',
    'pyramid_frontend>=0.4.2',
    'pyramid_uniform>=0.3.2',
    'pyramid_es>=0.3.0',
    'pyramid_mailer>=0.13',
    'pyramid_exclog>=0.7',
    'pyramid_cron>=0.1',
    'zope.sqlalchemy>=0.7.3',
    'waitress>=0.8.7',
    'webhelpers2>=2.0b5',
    'cryptacular>=1.4.1',
    'pymysql>=0.6.2',
    'premailer>=1.13',
    'gimlet>=0.5',
    'requests>=2.3.0',
    'lxml>=3.2.3',
    'Markdown>=2.5.2',
    'unidecode',
    'pytz',
    'iso3166',
    'Sphinx>=1.2',
    'sphinx-rtd-theme>=0.1.6',
    'WebHelpers2>=2.0',
    'dogpile.cache>=0.5.6',
    'FormEncode>=1.3',

    # Keep repoze.sendmail pinned at 4.1 to deal with this bug:
    # https://github.com/repoze/repoze.sendmail/issues/31
    'repoze.sendmail==4.1',
]


if not PY3:
    # Needed for uwsgi deployment with ini-paste-logged.
    requires.append('PasteScript>=1.7.5')


setup(name='zaphod',
      version='0.0',
      description='The Crowd Supply Platform',
      long_description='',
      # Using this invalid trove classifier prevents accidentally uploading
      # something to pypi.
      classifiers=['Private :: Do Not Upload'],
      url='http://github.com/crowdsupply/zaphod',
      keywords='',
      author='Scott Torborg, Joshua Lifton',
      author_email='support@crowdsupply.com',
      install_requires=requires,
      license='CONFIDENTIAL',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False,
      entry_points="""\
      [paste.app_factory]
      main = zaphod.main:main
      [console_scripts]
      initialize_zaphod_db = zaphod.scripts.initializedb:main
      migrate_zaphod_db = zaphod.scripts.migrate:main
      reindex_zaphod = zaphod.scripts.reindex:main
      """,
      )
