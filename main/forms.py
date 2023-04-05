from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from . import models, widgets
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory


logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your name")
    message = forms.CharField(
        max_length=600, label="Your message", widget=forms.Textarea
    )

    def send_mail(self):
        logger.info("Sending mail to customer service")
        message = f"From {self.cleaned_data['name']}\n{self.cleaned_data['message']}"
        send_mail(
            "Site message",
            message,
            "site@shelf.domain",
            ["customerservice@shelf.domain"],
            fail_silently=False,
        )


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(f"Sending signup email for email={self.cleaned_data['email']}")
        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            "Welcome to Shelf",
            message,
            "site@shelf.com",
            [self.cleaned_data["email"]],
            fail_silently=True,
        )


class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)

            if self.user is None:
                raise forms.ValidationError("Invalid email address or password")
            logger.info(f"Authentication successful for {email}")

        return self.cleaned_data

    def get_user(self):
        return self.user


BasketLineFormset = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=["quantity"],
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)


class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['shipping_address'].queryset = queryset
        self.fields['billing_address'].queryset = queryset