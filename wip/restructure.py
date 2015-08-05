import transaction

from sqlalchemy import create_engine

from zaphod import model


def sku_for_option_value_ids_loose(product, ov_ids):
    """
    From a list of option value IDs, return the corresponding SKU, or create a
    new one.

    If ``strict`` is set to False, allow incompletely-specified SKUs. Don't
    ever do this.
    """
    ov_ids = set(ov_ids)
    q = model.Session.query(model.SKU).filter_by(product=product)
    for ov_id in ov_ids:
        q = q.filter(model.SKU.option_values.any(id=ov_id))
    candidates = q.all()

    if len(candidates) == 1:
        return candidates[0]

    elif candidates:
        for sku in candidates:
            if set(ov.id for ov in sku.option_values) == ov_ids:
                return sku

    sku = model.SKU(product=product)
    for ov_id in ov_ids:
        ov = model.OptionValue.get(ov_id)
        sku.option_values.add(ov)
    model.Session.add(sku)
    return sku


def dump_sku(sku):
    if sku.option_values:
        return '%s: %s' % (sku.id, ', '.join(ov.description for ov in
                                             sku.option_values))
    else:
        return '%s: <no options>' % sku.id


class Remapping(object):
    def __init__(self, product):
        print('Remapping(%r)' % product)
        self.product = product
        self.ov_products = {}
        self.opt_drop = set()

    def _get_opt(self, product, opt_name):
        return [opt for opt in product.options
                if opt.name.lower() == opt_name.lower()][0]

    def _get_ov(self, product, opt_name, val_name):
        opt = self._get_opt(product, opt_name)
        return [val for val in opt.values
                if val.description.lower() == val_name.lower()][0]

    def add_product_when_selected(self, opt_name, val_name, new_product,
                                  qty=1, with_values=()):
        print('add_product_when_selected')
        option_value = self._get_ov(self.product, opt_name, val_name)
        new_values = [self._get_ov(new_product, oo, vv)
                      for oo, vv in with_values]
        this = self.ov_products.setdefault(option_value, [])
        this.append((new_product, qty, new_values))

    def drop_option(self, opt_name):
        print('drop_option')
        self.opt_drop.add(self._get_opt(self.product, opt_name))

    def _update_associated(self):
        print('_update_associated')
        for new_product, qty, with_values in self.ov_products.values():
            self.product.associated_products.add(new_product)

    def _create_new_item(self, orig_item, orig_ov, new_product, new_qty,
                         new_values, batch_map, item_map):
        print('_create_new_item(%r, %r, %r, %r, %r, ...)' % (
            orig_item.id, orig_ov.id, new_product.id, new_qty, new_values))
        # add new item with new product and new option
        # use price that was the price increase on the original value
        price = orig_ov.price_increase / new_qty
        new_item = model.CartItem(
            cart=orig_item.cart,
            product=new_product,
            qty_desired=new_qty,
            price_each=price,
            shipping_price=0,
            sku=sku_for_option_value_ids_loose(
                new_product, [ov.id for ov in new_values]),
            stage=orig_item.stage,
            _status=orig_item._status,
            batch=batch_map[orig_item.batch] if orig_item.batch else None,
            expected_ship_time=orig_item.expected_ship_time,
            shipped_time=orig_item.shipped_time,
            shipment=orig_item.shipment,
        )
        model.Session.add(new_item)

        q = model.Session.query(model.Item).filter_by(cart_item=orig_item)
        print('  looking for sku %s' % dump_sku(new_item.sku))
        for stock_item in q:
            print('    looking for stock item %s on acq %s' % (
                stock_item.id, stock_item.acquisition_id))
            for new_stock_item in item_map[stock_item]:
                new_stock_item.cart_item = new_item

        return price

    def _update_cart_item(self, item, cart, batch_map, item_map):
        print('_update_cart_item(%r, %r, ...)' % (item.id, cart.id))
        assert item.product == self.product
        after_values = set(item.sku.option_values)
        price_delta = 0
        for ov in item.sku.option_values:
            if ov in self.ov_products:
                for new_product, new_qty, new_values in self.ov_products[ov]:
                    price = self._create_new_item(item, ov, new_product,
                                                  new_qty, new_values,
                                                  batch_map, item_map)
                    price_delta += price
            if ov.option in self.opt_drop:
                after_values.discard(ov)

        # re-select item SKU based on removing the OVs that we popped out
        item.sku = sku_for_option_value_ids_loose(
            self.product, [ov.id for ov in after_values])

        # update item price to price minus price increases from migrated opts
        item.price_each -= price_delta
        model.Session.flush()

    def _create_new_batches(self):
        print('_create_new_batches')
        # make new batches for destination products
        todo_maps = set()
        for ov, replacements in self.ov_products.items():
            for dest_prod, qty, values in replacements:
                todo_maps.add((self.product, dest_prod))

        batch_map = {}
        for source_prod, dest_prod in todo_maps:
            # clone existing batches
            for orig_batch in source_prod.batches:
                new_batch = model.Batch(product=dest_prod,
                                        qty=0,
                                        ship_time=orig_batch.ship_time)
                batch_map[orig_batch] = new_batch

        return batch_map

    def _split_inventory(self):
        print('_split_inventory')
        item_map = {}
        # for each Item instance on a SKU in ov_products, split off a new item
        # that refers to the new product.

        # first build a map of orig SKUs to (list of) new SKUs that should have
        # inventory created for them.
        sku_map = {}
        for orig_sku in self.product.skus:
            print('mapping sku %s' % orig_sku.id)
            sku_map[orig_sku] = new_skus = []
            for ov, replacements in self.ov_products.items():
                if ov in orig_sku.option_values:
                    for dest_prod, qty, values in replacements:
                        new_sku = sku_for_option_value_ids_loose(
                            dest_prod, [ov.id for ov in values])
                        print('  sku map %s -> %s' % (dump_sku(orig_sku),
                                                      dump_sku(new_sku)))
                        new_skus.append(new_sku)

        # split all VendorOrderItems first
        voi_map = {}  # (voi, new_sku) -> new_voi
        for orig_sku, new_skus in sku_map.items():
            for voi in model.Session.query(model.VendorOrderItem).\
                    filter_by(sku=orig_sku):

                after_value_ids = set(ov for ov in voi.sku.option_values if
                                      ov.option not in self.opt_drop)
                voi.sku = sku_for_option_value_ids_loose(
                    orig_sku.product, after_value_ids)

                for new_sku in new_skus:
                    new_voi = model.VendorOrderItem(
                        order=voi.order,
                        qty_ordered=voi.qty_ordered,
                        sku=new_sku,
                        cost=0,
                    )
                    voi_map[(voi, new_sku)] = new_voi
                    model.Session.add(new_voi)

        # iterate over all Acquisitions that correspond to orig SKUs
        # for each one, create a new acquisition for each new SKU, and copy
        # items.
        for orig_sku, new_skus in sku_map.items():
            print('remapping acquisitions for %s' % dump_sku(orig_sku))
            for acq in model.Session.query(model.Acquisition).\
                    filter_by(sku=orig_sku):
                print('  acquisition %s' % acq.id)

                after_value_ids = set(ov for ov in acq.sku.option_values if
                                      ov.option not in self.opt_drop)
                acq.sku = sku_for_option_value_ids_loose(
                    orig_sku.product, after_value_ids)
                print('  new sku is %s' % dump_sku(acq.sku))

                for new_sku in new_skus:
                    print('  new acquisition for %s' % dump_sku(new_sku))
                    if isinstance(acq, model.VendorShipmentItem):
                        new_acq = model.VendorShipmentItem(
                            sku=new_sku,
                            acquisition_time=acq.acquisition_time,
                            vendor_shipment=acq.vendor_shipment,
                            vendor_order_item=voi_map[(acq.vendor_order_item,
                                                       new_sku)],
                        )
                    else:
                        assert isinstance(acq, model.InventoryAdjustment)
                        new_acq = model.InventoryAdjustment(
                            sku=new_sku,
                            acquisition_time=acq.acquisition_time,
                            qty_diff=acq.qty_diff,
                            reason=acq.reason,
                            user=acq.user,
                        )
                    model.Session.add(new_acq)
                    for orig_stock_item in acq.items:
                        print('    from item %d (sku %s)' % (
                            orig_stock_item.id, dump_sku(orig_sku)))
                        new_stock_item = model.Item(
                            create_time=orig_stock_item.create_time,
                            cart_item_id=None,
                            cost=0,
                            destroy_time=orig_stock_item.destroy_time,
                            # XXX destroy_adjustment_id ??
                        )
                        item_map.setdefault(orig_stock_item, []).\
                            append(new_stock_item)
                        new_acq.items.append(new_stock_item)
                        model.Session.flush()
                        print('      created new item %s' % new_stock_item.id)

        return item_map

    def _finalize_batches(self, batch_map):
        print('_finalize_batches')
        for new_batch in batch_map.values():
            new_batch.qty = new_batch.qty_claimed

    def _finalize_skus(self):
        print('_finalize_skus')
        # delete any SKUs which are associated with dropped options
        for opt in self.opt_drop:
            q = model.Session.query(model.SKU).\
                join(model.SKU.option_values).\
                filter(model.OptionValue.option == opt)
            for sku in q.all():
                print('deleting %s' % dump_sku(sku))
                model.Session.delete(sku)
                model.Session.flush()

    def _drop_options(self):
        print('_drop_options')
        for opt in self.opt_drop:
            for val in opt.values:
                model.Session.delete(val)
            model.Session.delete(opt)
            model.Session.flush()

    def apply(self):
        print('apply')
        batch_map = self._create_new_batches()
        item_map = self._split_inventory()

        # update items
        q = model.Session.query(model.CartItem, model.Cart).\
            join(model.Cart.items).\
            filter(model.CartItem.product == self.product)
        for item, cart in q:
            self._update_cart_item(item, cart, batch_map, item_map)

        self._finalize_batches(batch_map)
        self._finalize_skus()
        self._drop_options()


def remap_usb_armory():
    product_usb_armory = model.Product.get(773)
    product_extra_card = model.Product.get(774)
    product_host_adapter = model.Product.get(782)
    product_enclosure = model.Product.get(849)

    all_products = [
        product_usb_armory,
        product_extra_card,
        product_host_adapter,
        product_enclosure,
    ]

    remapping = Remapping(product_usb_armory)

    for choice, qty in [('one', 1), ('two', 2), ('three', 3)]:
        remapping.add_product_when_selected('usb host adapters',
                                            choice, product_host_adapter,
                                            qty=qty)

    remapping.drop_option('usb host adapters')

    for size in ('4GB', '8GB', '16GB', '32GB'):
        choice = '%s w/ debian installation' % size
        remapping.add_product_when_selected(
            'microsd card', choice, product_extra_card,
            with_values=[('capacity', choice)])

    remapping.drop_option('microsd card')

    remapping.apply()

    model.Session.flush()

    for product in all_products:
        product.published = True
        product.update_in_stock()
        for other_product in all_products:
            if product != other_product:
                product.associated_products.add(other_product)


"""
Things to check to verify that this script ran correctly for the USB Armory:

    - USB Armory product options should be gone.
    - No new batches for Host Adapter or SD Card should be oversubscribed.
    - Stock status of USB Armory products should not change.

    http://localhost:6543/admin/order/20604
    should contain:
        - a stock USB Armory for $130, shipped on shipment 6994
        - a stock 16GB microSD cardf for $23, shipped on shipment 6994
        - a preorder enclosure for $15, waiting for items

    http://localhost:6543/admin/order/18421
    should contain
        - a crowdfunding USB armory for $130, shipping price of $10

    http://localhost:6543/admin/order/18574
    should contain
        - a crowdfunding USB armory for $130, shipped on shipment 5608
        - a crowdfunding USB armory for $130, shipped on shipment 5608 (dupe)
        - a crowdfunding 8GB microSD card for $18, shipped on shipment 5608

    http://localhost:6543/admin/order/19248
    should contain
        - a crowdfunding USB armory for $130, shipped on shipment 6063
        - a crowdfunding host ad. qty 3 for $10, shipped on shipment 6063
        - a crowdfunding 16GB microSD card for $23, shipped on shipment 6063
        - a crowdfunding host ad. qty 1 for $10, shipped on shipment 6063
"""


if __name__ == '__main__':
    url = 'mysql+pymysql://zaphod:zaphod@localhost/zaphod?charset=utf8'
    engine = create_engine(url)
    model.init_model(engine, read_only=False)

    with transaction.manager:
        remap_usb_armory()
