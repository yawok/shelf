from django.test import TestCase
from main import models
from decimal import Decimal


class TestModels(TestCase):
    def test_active_manager_works(self):
        models.Product.objects.create(
            name='A random product 1',
            price=Decimal("5.50")
        )
        models.Product.objects.create(
            name='A random product 2',
            price=Decimal("5.50")
        )
        models.Product.objects.create(
            name='A random product 3',
            price=Decimal("5.50"), 
            active=False
        )
        
        self.assertEqual(len(models.Product.objects.active()), 2)