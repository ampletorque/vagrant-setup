from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import FunctionalBase


class TestBrowse(FunctionalBase):

    def test_browse(self):
        resp = self.app.get('/browse')
        self.assertIn('Lifestyle', resp.body)
        self.assertNotIn('Unlisted Tag', resp.body)
