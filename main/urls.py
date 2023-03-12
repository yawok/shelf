from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('about-us/', TemplateView.as_view(template_name="about_us.html"), name='about-us'),
    path('contact-us/', views.ContactUsForm.as_view(), name='contact-us'),
]
