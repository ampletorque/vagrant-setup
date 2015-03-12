from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def update_carts(system):
    """
    Release item and batch reservations for carts that have been stale for 30
    minutes.
    """
    # Get a list of cart items which are:
    # - associated with stale carts
    # - have no order
    # - have a batch set OR have items reserved
    # ... locking for update

    # Set cart items to no batch, and de-reserve items.


def includeme(config):
    config.add_cron_task(update_carts, min=range(0, 60, 5))
