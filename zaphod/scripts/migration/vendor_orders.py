from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model


def get_creator_id(old_vo):
    creators = set()
    for voi in old_vo.items:
        assert voi.product.project, "voi %d has no project" % voi.id
        creators.add(voi.product.project.creator)
    assert len(creators) == 1, \
        "not one creatorfor order %d: %r" % (old_vo.id,
                                             [creator.id for creator in
                                              creators])
    creator = list(creators)[0]
    assert creator
    return creator.id


def migrate_vendor_orders(settings, product_map, option_value_map):
    for old_vo in scrappy_meta.Session.query(scrappy_model.VendorOrder):
        print("  vendor order %s" % old_vo.id)
        vo = model.VendorOrder(
            status=old_vo.status.value,
            id=old_vo.id,
            creator_id=get_creator_id(old_vo),
        )
        model.Session.add(vo)
        for old_voi in old_vo.items:
            print("    voi %d" % old_voi.id)
            sku = model.sku_for_option_value_ids_sloppy(
                product_map[old_voi.product],
                set(option_value_map[old_ov].id
                    for old_ov in old_voi.option_values))
            voi = model.VendorOrderItem(
                qty_ordered=old_voi.qty_ordered,
                cost=old_voi.cost,
                sku=sku,
            )
            vo.items.append(voi)
