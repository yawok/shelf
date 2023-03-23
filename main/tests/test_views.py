from django.test import TestCase
from django.urls import reverse
from main import forms, models
from decimal import Decimal
from django.contrib import auth
from unittest.mock import patch

class TestPage(TestCase):
    def test_home_page_works(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Shelf")

    def test_about_us_page_works(self):
        response = self.client.get(reverse("about-us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about_us.html")
        self.assertContains(response, "Shelf")
    
    def test_contact_us_page_workd(self):
        response = self.client.get(reverse('contact-us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form.html")
        self.assertContains(response, "Shelf")
        self.assertIsInstance(response.context['form'], forms.ContactForm)
        

class TestProductListPage(TestCase):
    def test_product_page_returns_active(self):
        models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
            slug="the-cathedral"
        )
        models.Product.objects.create(
            name="The treasure island",
            price=Decimal("10.00"),
            slug="the-treasure",
            active=False,
        )
        
        response = self.client.get(
            reverse('products', kwargs={'tag': 'all'}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shelf')

        product_list = models.Product.objects.active().order_by('name')
        self.assertEqual(list(response.context['object_list']), list(product_list),)
        
    
    def test_product_page_filters_by_tag_and_active(self):
        product = models.Product.objects.create(
            name="Python crash course",
            price=Decimal("10.00"),
            slug="python-crash-course"
        )
        product.tags.create(
             name='Open Source', slug='open-source'
        )
        models.Product.objects.create(
            name="Cell",
            price=Decimal("10.00"),
        )
        
        response = self.client.get(
            reverse('products', kwargs={'tag':'open-source'}
        ))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shelf')
        
        product_list = models.Product.objects.active().filter(tags__slug='open-source').order_by('name')
        
        self.assertEqual(list(product_list), list(response.context['object_list']))
    
    
class TestUserCreationForm(TestCase):
    def test_user_form_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "Shelf")
        self.assertIsInstance(response.context['form'], forms.UserCreationForm)
    
    def test_signup_page_submition_works(self):
        post_data = {
            "email": "user@example.com",
            "password1": "this is a random password",
            "password2": "this is a random password"
        }
        
        with patch.object(forms.UserCreationForm, 'send_mail') as mock_send:
            response = self.client.post(reverse("signup"), post_data)
        
            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                models.User.objects.filter(
                    email="user@example.com"
                ).exists()
            )
            self.assertTrue(auth.get_user(self.client).is_authenticated)
            mock_send.assert_called_once()