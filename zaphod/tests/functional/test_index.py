from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import FunctionalBase


class TestIndex(FunctionalBase):

    def test_index(self):
        resp = self.app.get('/')
        resp.mustcontain('Recently')
