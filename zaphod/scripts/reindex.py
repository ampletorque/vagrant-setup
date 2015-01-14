from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
import sys

import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import bootstrap, setup_logging

from .. import es


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
    env = bootstrap(config_uri)
    with transaction.manager:
        es.hard_reset(env['registry'])
