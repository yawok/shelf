from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from . import models


logger = logging.getLogger(__name__)

class ContactForm(forms.Form):
	name = forms.CharField(max_length=100, label="Your name")
	message = forms.CharField(max_length=600, label="Your message", widget=forms.Textarea)
	
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
		fields = ('email',)
		field_classes = {'email': UsernameField}
	
	def send_mail(self):
		logger.INFO(f"Sending signup email for email={self.cleaned_data['email']}")
		message = f"Welcome {self.cleaned_data['email']}"
		send_mail(
			"Welcome to Shelf",
			message,
			"site@shelf.com",
			[self.cleaned_data['email']],
			fail_silently=True
		)
