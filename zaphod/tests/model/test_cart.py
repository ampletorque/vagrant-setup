from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import transaction

from ... import model

from .base import ModelTest


class TestCart(ModelTest):
    @classmethod
    def _setup_once_data(cls):
        cart = model.Cart(
        )
        model.Session.add(cart)
