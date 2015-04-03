from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import timedelta

from . import model


def update_carts(system):
    """
    Release item and batch reservations for carts that have been stale for 30
    minutes.
    """
    cutoff = model.utcnow() - timedelta(minutes=30)

    # Get a list of cart items which are:
    # - associated with stale carts
    # - have not checked out
    # - have not already been expired
    # ... locking for update
    q = model.Session.query(model.CartItem).\
        join(model.CartItem.cart).\
        filter(model.Cart.updated_time < cutoff).\
        filter(model.CartItem.status == 'cart').\
        filter(model.CartItem.stage != model.CartItem.INACTIVE).\
        with_for_update()

    # Set cart items to no batch, and de-reserve items.
    for ci in q:
        ci.expire()


def includeme(config):
    config.add_cron_task(update_carts, min=range(0, 60, 5))
