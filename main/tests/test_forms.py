from django.test import TestCase
from django.core import mail
from main import forms


class TestForm(TestCase):
    def test_valid_contact_us_forms_sends_email(self):
        form = forms.ContactForm(
            {
                "name": "Kenneth Obeng",
                "message": "I haven't recieved my order details yet. Help!",
            }
        )
        self.assertTrue(form.is_valid())
        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Site message")
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_form(self):
        form = forms.ContactForm(
            {
                "message": "I haven't recieved my order details yet. Help!",
            }
        )
        self.assertFalse(form.is_valid())

    def test_valid_signup_form_sends_email(self):
        form = forms.UserCreationForm(
            {
                "email": "test@example.com",
                "password1": "this is a random password",
                "password2": "this is a random password",
            }
        )
        self.assertTrue(form.is_valid())
        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to Shelf")
        self.assertGreaterEqual(len(cm.output), 1)
