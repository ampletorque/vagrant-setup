from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model


def migrate_inventory_adjustments():
    for old_adj in \
            scrappy_meta.Session.query(scrappy_model.InventoryAdjustment):
        adj = model.InventoryAdjustment(
            id=old_adj.id,
            qty_diff=old_adj.qty_diff,
            user_id=old_adj.account_id,
            reason=old_adj.reason,
        )
        model.Session.add(adj)
    model.Session.flush()


def migrate_items():
    for old_item in scrappy_meta.Session.query(scrappy_model.Item):
        item = model.Item(
            id=old_item.id,
            acquisition_id=old_item.acquisition_id,
            create_time=old_item.create_time,
            cost=old_item.cost,
            destroy_time=old_item.destroy_time,
            destroy_adjustment_id=old_item.destroy_adjustment_id,
        )
        model.Session.add(item)
    model.Session.flush()
