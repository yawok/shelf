from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class ProductTag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Product(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(ProductTag, blank=True)

    objects = ActiveManager()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Address(models.Model):
    SUPPORTED_COUNTRIES = (
        ("gh", "Ghana"),
        ("us", "United States"),
        ("uk", "United Kingdom"),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    address1 = models.CharField("Address line 1", max_length=120)
    address2 = models.CharField("Address line 2", max_length=120, blank=True)
    zip_code = models.CharField("Zip/Postal Code", max_length=12)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=3, choices=SUPPORTED_COUNTRIES)
    
    def __str__(self):
        return ", ".join([self.name, self.address1, self.address2, self.zipcode, self.city, self.country])
    

class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, "Open"), (SUBMITTED, "Submitted"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)
    
    def is_empty(self):
        return self.basketline_set.all().count() == 0
    
    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())
    
    
class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    
class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (PAID, "Paid"), (DONE, "Done"))
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    
    billing_name = models.CharField(max_length=120)
    billing_address1 = models.CharField(max_length=120)
    billing_address2 = models.CharField(max_length=120, blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=120)
    billing_country = models.CharField(max_length=3)

    shipping_name = models.CharField(max_length=120)
    shipping_address1 = models.CharField(max_length=120)
    shipping_address2 = models.CharField(max_length=120, blank=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=120)
    shipping_country = models.CharField(max_length=3)
    
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
class Orderline(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = ((NEW, "New"), (PROCESSING, "Processing"), (SENT, "Sent"), (CANCELLED, "Cancelled"))
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    