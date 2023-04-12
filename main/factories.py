import factory
import factory.fuzzy
from . import models

class UserFactory(factory.django.DjangoModelFactory):
    email = 'user@example.com'
    
    class Meta:
        models = models.User
        django_get_or_create = ('email',)


class ProductFactory(factory.django.DjangoModelFactory):
    price = factory.fuzzy.FuzzyDecimal(1.0, 1000.0, 2)

    class Meta:
        models = models.Product
        

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        models = models.Address