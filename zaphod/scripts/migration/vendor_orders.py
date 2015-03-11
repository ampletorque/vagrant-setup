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
            id=old_vo.id,
            reference=old_vo.order_num,
            description=old_vo.description,
            status=old_vo.status.value,
            creator_id=get_creator_id(old_vo),
            placed_by_id=old_vo.placed_by_id,
            placed_time=old_vo.placed_time,
            updated_by_id=old_vo.updated_by_id,
            updated_time=old_vo.updated_time,
            created_by_id=old_vo.created_by_id,
            created_time=old_vo.created_time,
        )
        model.Session.add(vo)
        vendor_shipment_map = {}
        for old_vs in old_vo.shipments:
            print("    vs %d" % old_vs.id)
            vs = model.VendorShipment(
                id=old_vs.id,
                description=old_vs.description,
                updated_by_id=old_vs.updated_by_id,
                updated_time=old_vs.updated_time,
                created_by_id=old_vs.created_by_id,
                created_time=old_vs.created_time,
            )
            vo.shipments.append(vs)
            vendor_shipment_map[old_vs] = vs
        for old_voi in old_vo.items:
            print("    voi %d" % old_voi.id)
            sku = model.sku_for_option_value_ids_sloppy(
                product_map[old_voi.product],
                set(option_value_map[old_ov].id
                    for old_ov in old_voi.option_values))
            voi = model.VendorOrderItem(
                id=old_voi.id,
                qty_ordered=old_voi.qty_ordered,
                cost=old_voi.cost,
                sku=sku,
            )
            vo.items.append(voi)
            for old_vsi in old_voi.vendor_shipment_items:
                print("      vsi %d" % old_vsi.id)
                vs = vendor_shipment_map[old_vsi.vendor_shipment]
                vsi = model.VendorShipmentItem(
                    id=old_vsi.id,
                    vendor_order_item=voi,
                    vendor_shipment=vs,
                    sku=sku,
                )
                model.Session.add(vsi)
