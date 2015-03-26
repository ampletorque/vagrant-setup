from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

from ... import helpers as h


class TestHelpers(TestCase):

    def test_grouper_even_split(self):
        self.assertEqual(list(h.grouper(3, range(9))),
                         [[0, 1, 2], [3, 4, 5], [6, 7, 8]])

    def test_grouper_uneven_split(self):
        self.assertEqual(list(h.grouper(4, range(6))),
                         [[0, 1, 2, 3], [4, 5]])

    def test_grouper_makes_iterable(self):
        try:
            iter(h.grouper(5, [1, 2, 3, 4, 5]))
        except TypeError:
            raise AssertionError('should be iterable')

    def test_grouper_row_larger_than_input(self):
        self.assertEqual(list(h.grouper(5, ['f', 'bar', 'baz'])),
                         [['f', 'bar', 'baz']])

    def test_prettify_plain(self):
        self.assertEqual(h.prettify('joe_user'), 'Joe user')

    def test_prettify_multi(self):
        self.assertEqual(h.prettify('foo_bar_baz_quux'), 'Foo bar baz quux')

    def test_prettify_num(self):
        self.assertEqual(h.prettify(123), '123')

    def test_currency_small(self):
        self.assertEqual(h.currency(123.45), '$123.45')

    def test_currency_bigger(self):
        self.assertEqual(h.currency(12345.67), '$12,345.67')

    def test_currency_int(self):
        self.assertEqual(h.currency(1234), '$1,234.00')

    def test_currency_huge(self):
        self.assertEqual(h.currency(1234567890.12), '$1,234,567,890.12')

    def test_commas_small(self):
        self.assertEqual(h.commas(123.45), '123')
        self.assertEqual(h.commas(123.45, decimal=True), '123.45')

    def test_commas_bigger(self):
        self.assertEqual(h.commas(12345.67), '12,345')
        self.assertEqual(h.commas(12345.67, decimal=True), '12,345.67')

    def test_commas_int(self):
        self.assertEqual(h.commas(1234), '1,234')
        self.assertEqual(h.commas(1234, decimal=True), '1,234.00')

    def test_commas_huge(self):
        self.assertEqual(h.commas(1234567890.12), '1,234,567,890')
        self.assertEqual(h.commas(1234567890.12, decimal=True),
                         '1,234,567,890.12')
