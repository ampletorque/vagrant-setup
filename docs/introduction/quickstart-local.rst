Quick Start with Local Development Server
=========================================

Install Dependencies
--------------------

These services are required:

- MySQL or MariaDB
- Redis
- Elasticsearch
- lessc (via the ``less`` npm package)
- requirejs (via the ``requirejs`` npm package)
- autoprefixer (via the ``autoprefixer`` npm package)

Install Zaphod
--------------

Checkout the repo::

    $ git clone git@github.com:crowdsupply/zaphod.git

Install the package::

    $ cd zaphod
    $ python setup.py develop

Bootstrap a Database
--------------------

First, create the Zaphod required databases in MySQL by running the
``site/conf/dbsetup.sql`` SQL script as root.

There are two ways to bootstrap a working database to run the app:

Create the bare schema from scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A population script is included which will create an example DB with some test
data::

    $ cd site/conf
    $ initialize_zaphod_db development.ini

Migrate from a legacy scrappy database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During early development, a migration script will be maintained to populate an
initial database from a legacy scrappy-backed DB. This requires having the
``scrappy`` and ``crowdsupply`` packages correctly installed and a local
up-to-date ``crowdsupply`` database. ::

    $ migrate_zaphod_db development.ini

Note that this migration script will be removed from the repo once the live
site has been migrated.

Copy the live production database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply dump the SQL from the live website, and load it locally. ::

    myserver$ mysqldump -uroot zaphod > zaphod.sql
    local$ mysql -uroot zaphod < zaphod.sql

Development and Deployment
--------------------------

To run the app locally, use ``pserve``::

    $ cd site/conf
    $ pserve --reload development.ini

View the website in a browser at http://localhost:6543.

The app server will be automatically restarted on changes to files.
