from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

import transaction

from webtest import TestApp

from ...main import main
from ... import model, es

from .. import data
from ..settings import settings


app = main({}, **settings)


def setup():
    model.Base.metadata.drop_all()
    model.Base.metadata.create_all()

    with transaction.manager:
        root_user = model.User(
            name=u'Bot',
            email='root@zaphod.local',
        )
        root_user.update_password('root')
        model.Session.add(root_user)

        data.populate_content()

    es.hard_reset(app.registry)


class FunctionalBase(TestCase):

    def setUp(self):
        self.app = TestApp(app)
