from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

from ... import model


class TestCreator(TestCase):
    def test_display_url(self):
        creator = model.Creator(
            home_url='http://www.spaghetti.org/monsters/',
        )
        self.assertEqual(creator.display_url,
                         'spaghetti.org/monsters')

        creator = model.Creator(
            home_url='https://www.example.com',
        )
        self.assertEqual(creator.display_url,
                         'example.com')

        creator = model.Creator(
            home_url='https://what.craziness.net/foo/bar',
        )
        self.assertEqual(creator.display_url,
                         'what.craziness.net/foo/bar')

        creator = model.Creator()
        self.assertIsNone(creator.display_url)
