from ... import model

from .base import ModelTest


class TestVendor(ModelTest):
    @classmethod
    def _setup_once_data(cls):
        vendor = model.Vendor(name=u'Test Vendor')
        model.Session.add(vendor)

        vendor_order = model.VendorOrder(vendor=vendor)
        model.Session.add(vendor_order)

        model.Session.flush()

        cls.vendor_id = vendor.id
        cls.vendor_order_id = vendor_order.id
