from django.test import TestCase
from main import models, factories
from decimal import Decimal


class TestProduct(TestCase):
    def test_active_manager_works(self):
        factories.ProductFactory.create_batch(2, active=True)
        factories.ProductFactory(active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)


class TestBasket(TestCase):
    def test_create_order_works(self):
        p1 = factories.ProductFactory()
        p2 = factories.ProductFactory()
        user = factories.UserFactory()
        billing = factories.AddressFactory(user=user)
        shipping = factories.AddressFactory(user=user)
        basket = models.Basket.objects.create(user=user)
        models.BasketLine.objects.create(basket=basket, product=p1)
        models.BasketLine.objects.create(basket=basket, product=p2, quantity=2)

        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(shipping, billing)

        self.assertGreaterEqual(len(cm.output), 1)

        order.refresh_from_db()

        self.assertEqual(order.user, user)
        self.assertEqual(order.shipping_name, shipping.name)
        self.assertEqual(order.billing_name, billing.name)
        self.assertEqual(order.lines.all().count(), 3)
        lines = order.lines.all()
        print(lines)
        self.assertEqual(lines[0].product, p1)
        self.assertEqual(lines[1].product, p2)
        self.assertEqual(lines[2].product, p2)
