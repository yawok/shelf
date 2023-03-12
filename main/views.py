from django.shortcuts import render
from django.views.generic.edit import FormView
from main.forms import ContactForm


class ContactUsForm(FormView):
    template_name = 'contact_form.html'
    form_class = ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)
