from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

import transaction

from ... import model

from .base import ModelTest
from .mocks import patch_utcnow


class TestCart(ModelTest):

    def _add_item(self, cart, product, qty):
        ci = model.CartItem(
            cart=cart,
            product=product,
            qty_desired=qty,
            sku=model.sku_for_option_value_ids(product, []),
            price_each=product.price,
            shipping_price=0,
            stage=model.CartItem.INACTIVE,
        )
        cart.items.append(ci)
        return ci

    def _make_products(self, project, accepts_preorders=True):
        non_physical_product = model.Product(
            name='Non-Physical Product',
            non_physical=True,
            published=True,
            accepts_preorders=accepts_preorders,
        )
        project.products.append(non_physical_product)

        qty_limited_product = model.Product(
            name='Qty Limited Product',
            published=True,
            accepts_preorders=accepts_preorders,
        )
        project.products.append(qty_limited_product)
        qty_limited_product.batches.append(model.Batch(
            qty=5,
            ship_time=datetime(2014, 11, 15),
        ))
        qty_limited_product.batches.append(model.Batch(
            qty=5,
            ship_time=datetime(2014, 12, 15),
        ))

        qty_unlimited_product = model.Product(
            name='Qty Unlimited Product',
            published=True,
            accepts_preorders=accepts_preorders,
        )
        project.products.append(qty_unlimited_product)
        qty_unlimited_product.batches.append(model.Batch(
            qty=None,
            ship_time=datetime(2014, 9, 20),
        ))
        return non_physical_product, qty_limited_product, qty_unlimited_product

    def _make_project_fixture(self, name, start_time, end_time):
        creator = model.Creator(name='Test Creator')
        model.Session.add(creator)

        project = model.Project(
            creator=creator,
            name=name,
            start_time=start_time,
            end_time=end_time,
            published=True,
            accepts_preorders=True,
        )
        model.Session.add(project)

        non_physical_product, qty_limited_product, qty_unlimited_product = \
            self._make_products(project)

        cart = model.Cart()
        model.Session.add(cart)

        non_physical_ci = self._add_item(cart, non_physical_product, 2)
        qty_limited_ci = self._add_item(cart, qty_limited_product, 8)
        qty_unlimited_ci = self._add_item(cart, qty_unlimited_product, 3)
        model.Session.flush()

        non_physical_ci_id = non_physical_ci.id
        qty_limited_ci_id = qty_limited_ci.id
        qty_unlimited_ci_id = qty_unlimited_ci.id
        transaction.commit()
        return non_physical_ci_id, qty_limited_ci_id, qty_unlimited_ci_id

    def test_crowdfunding_refresh(self):
        non_physical_ci_id, qty_limited_ci_id, qty_unlimited_ci_id = \
            self._make_project_fixture(
                name='Test CF Project',
                start_time=datetime(2014, 4, 1),
                end_time=datetime(2014, 5, 12),
            )

        non_physical_ci = model.CartItem.get(non_physical_ci_id)
        qty_limited_ci = model.CartItem.get(qty_limited_ci_id)
        qty_unlimited_ci = model.CartItem.get(qty_unlimited_ci_id)

        cart = non_physical_ci.cart

        with patch_utcnow(2014, 4, 20):
            cart.refresh()
            self.assertEqual(non_physical_ci.stage,
                             model.CartItem.CROWDFUNDING)
            self.assertEqual(non_physical_ci.qty_desired, 2)
            self.assertIsNone(non_physical_ci.batch)

            self.assertEqual(qty_limited_ci.stage, model.CartItem.CROWDFUNDING)
            self.assertEqual(qty_limited_ci.qty_desired, 8)
            self.assertIsNotNone(qty_limited_ci.batch)

            self.assertEqual(qty_unlimited_ci.stage,
                             model.CartItem.CROWDFUNDING)
            self.assertEqual(qty_unlimited_ci.qty_desired, 3)
            self.assertIsNotNone(qty_unlimited_ci.batch)

            for ci in cart.items:
                ci.expire()
            self.assertEqual(non_physical_ci.stage, model.CartItem.INACTIVE)
            self.assertEqual(qty_limited_ci.stage, model.CartItem.INACTIVE)
            self.assertEqual(qty_unlimited_ci.stage, model.CartItem.INACTIVE)

            self.assertEqual(non_physical_ci.qty_desired, 2)
            self.assertEqual(qty_limited_ci.qty_desired, 8)
            self.assertEqual(qty_unlimited_ci.qty_desired, 3)

            self.assertIsNone(non_physical_ci.batch)
            self.assertIsNone(qty_limited_ci.batch)
            self.assertIsNone(qty_unlimited_ci.batch)

    def test_available_refresh(self):
        non_physical_ci_id, qty_limited_ci_id, qty_unlimited_ci_id = \
            self._make_project_fixture(
                name='Test Pre-Order Project',
                start_time=datetime(2014, 3, 1),
                end_time=datetime(2014, 4, 10),
            )

        # add stock product

        # add stock CI

        non_physical_ci = model.CartItem.get(non_physical_ci_id)
        qty_limited_ci = model.CartItem.get(qty_limited_ci_id)
        qty_unlimited_ci = model.CartItem.get(qty_unlimited_ci_id)

        cart = non_physical_ci.cart

        with patch_utcnow(2014, 4, 20):
            cart.refresh()
            self.assertEqual(non_physical_ci.stage,
                             model.CartItem.STOCK)
            self.assertEqual(non_physical_ci.qty_desired, 2)
            self.assertIsNone(non_physical_ci.batch)

            self.assertEqual(qty_limited_ci.stage, model.CartItem.PREORDER)
            self.assertEqual(qty_limited_ci.qty_desired, 8)
            self.assertIsNotNone(qty_limited_ci.batch)

            self.assertEqual(qty_unlimited_ci.stage,
                             model.CartItem.PREORDER)
            self.assertEqual(qty_unlimited_ci.qty_desired, 3)
            self.assertIsNotNone(qty_unlimited_ci.batch)

            for ci in cart.items:
                ci.expire()
            self.assertEqual(non_physical_ci.stage, model.CartItem.INACTIVE)
            self.assertEqual(qty_limited_ci.stage, model.CartItem.INACTIVE)
            self.assertEqual(qty_unlimited_ci.stage, model.CartItem.INACTIVE)

            self.assertEqual(non_physical_ci.qty_desired, 2)
            self.assertEqual(qty_limited_ci.qty_desired, 8)
            self.assertEqual(qty_unlimited_ci.qty_desired, 3)

            self.assertIsNone(non_physical_ci.batch)
            self.assertIsNone(qty_limited_ci.batch)
            self.assertIsNone(qty_unlimited_ci.batch)
