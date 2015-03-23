from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model

from . import utils


def migrate_vendors(settings, user_map):
    for old_vendor in scrappy_meta.Session.query(scrappy_model.Vendor):
        print("  vendor %s" % old_vendor.id)
        vendor = model.Vendor(
            id=old_vendor.id,
            name=old_vendor.name,
            active=old_vendor.active,
            mailing=utils.convert_address(old_vendor.mailing),
            created_by=user_map[old_vendor.created_by],
            created_time=old_vendor.created_time,
            updated_by=user_map[old_vendor.updated_by],
            updated_time=old_vendor.updated_time,
        )
        model.Session.add(vendor)


def migrate_vendor_orders(settings, product_map, option_value_map, user_map):
    for old_vo in scrappy_meta.Session.query(scrappy_model.VendorOrder):
        print("  vendor order %s" % old_vo.id)
        vo = model.VendorOrder(
            id=old_vo.id,
            vendor_id=old_vo.vendor_id,
            reference=old_vo.order_num,
            description=old_vo.description,
            status=old_vo.status.value,
            placed_by=user_map[old_vo.placed_by],
            placed_time=old_vo.placed_time,
            updated_by=user_map[old_vo.updated_by],
            updated_time=old_vo.updated_time,
            created_by=user_map[old_vo.created_by],
            created_time=old_vo.created_time,
        )
        model.Session.add(vo)
        vendor_shipment_map = {}
        for old_vs in old_vo.shipments:
            print("    vs %d" % old_vs.id)
            vs = model.VendorShipment(
                id=old_vs.id,
                description=old_vs.description,
                updated_by=user_map[old_vs.updated_by],
                updated_time=old_vs.updated_time,
                created_by=user_map[old_vs.created_by],
                created_time=old_vs.created_time,
            )
            vo.shipments.append(vs)
            vendor_shipment_map[old_vs] = vs
        for old_voi in old_vo.items:
            print("    voi %d" % old_voi.id)
            sku = utils.sku_for_option_values(
                product_map[old_voi.product],
                set(option_value_map[old_ov]
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
