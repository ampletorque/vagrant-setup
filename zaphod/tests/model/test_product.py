from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

from ... import model


class TestProduct(TestCase):

    def test_option_deletes(self):
        product = model.Product()
        model.Session.add(product)

        option = model.Option(
            name='Size',
        )
        product.options.append(option)

        option.values.append(model.OptionValue(
            name='S',
        ))

        option.values.append(model.OptionValue(
            name='M',
        ))

        option.values.append(model.OptionValue(
            name='L',
        ))

        # XXX
