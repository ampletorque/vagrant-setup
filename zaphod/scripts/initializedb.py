from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os.path
import sys

import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from .. import model


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    model.Session.configure(bind=engine)
    model.Base.metadata.drop_all(engine)
    model.Base.metadata.create_all(engine)

    with transaction.manager:
        root_user = model.User(
            name=u'Root',
            email='root@zaphod.local',
        )
        root_user.update_password('root')
        model.Session.add(root_user)

        creator = model.Creator(
            name=u'Galactic Government',
            published=True,
            listed=True,
        )
        model.Session.add(creator)
        creator.update_path(creator.generate_path())

        project = model.Project(
            creator=creator,
            name=u'Infinite Improbability Drive',
            published=True,
            listed=True,
        )
        model.Session.add(project)
        project.update_path(project.generate_path())
