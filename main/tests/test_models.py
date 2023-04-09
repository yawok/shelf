from django.test import TestCase
from main import models
from decimal import Decimal


class TestProduct(TestCase):
    def test_active_manager_works(self):
        models.Product.objects.create(name="A random product 1", price=Decimal("5.50"))
        models.Product.objects.create(name="A random product 2", price=Decimal("5.50"))
        models.Product.objects.create(
            name="A random product 3", price=Decimal("5.50"), active=False
        )

        self.assertEqual(len(models.Product.objects.active()), 2)


class TestBasket(TestCase):
    def test_create_order_works(self):
        p1 = models.Product.objects.create(
            name="A tale of 2 cities", price=Decimal("33.5")
        )
        p2 = models.Product.objects.create(name="Cell", price=Decimal("24.00"))
        user = models.User.objects.create_user(
            email="user@example.com", password="1randomDud6"
        )
        billing = models.Address.objects.create(
            user=user,
            name="Random Dude",
            address1="Dakwadwom",
            address2="RishRishe",
            zip_code="00012",
            city="Kumasi",
            country="gh",
        )
        shipping = models.Address.objects.create(
            user=user,
            name="Random Dude's brother",
            address1="Dakwadwom",
            address2="RishRishe",
            zip_code="00012",
            city="Kumasi",
            country="gh",
        )
        basket = models.Basket.objects.create(user=user)
        models.BasketLine.objects.create(basket=basket, product=p1)
        models.BasketLine.objects.create(basket=basket, product=p2, quantity=2)

        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(shipping, billing)

        self.assertGreaterEqual(len(cm.output), 1)

        order.refresh_from_db()

        self.assertEqual(order.user, user)
        self.assertEqual(order.shipping_name, "Random Dude's brother")
        self.assertEqual(order.billing_name, "Random Dude")
        self.assertEqual(order.lines.all().count(), 3)
        lines = order.lines.all()
        self.assertEqual(lines[0], p1)
        self.assertEqual(lines[1], p2)
        self.assertEqual(lines[2], p2)
