from django.shortcuts import render
from django.views.generic.edit import FormView
from main import forms, models
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class ContactUsForm(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs["tag"]
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()
        return products.order_by("name")

class SignupView(FormView):
    template_name = "main/signup.html"
    form_class = forms.UserCreationForm
    
    def get_success_url(self):
        redirect_to = self.request.GET.get('next', '/')
        return redirect_to
    
    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get('email')
        raw_password = self.cleaned_data.get('raw_password')
        logger.INFO(f"New signup for {email} through SignupView.")
        user = authenticate(email=email, raw_password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You have signed up successfully.")
        
        return response