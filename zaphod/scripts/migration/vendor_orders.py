from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model


def migrate_vendor_orders():
    for old_vo in scrappy_meta.Session.query(scrappy_model.VendorOrder):
        print("  vendor order %s" % old_vo.id)
        vo = model.VendorOrder(
            id=old_vo.id,
        )
        model.Session.add(vo)
