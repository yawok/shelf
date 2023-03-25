from django.urls import path
from django.views.generic import TemplateView, DetailView
from . import views
from django.conf.urls.static import static
from django.conf import settings
from main import models, forms
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path(
        "about-us/",
        TemplateView.as_view(template_name="about_us.html"),
        name="about-us",
    ),
    path("contact-us/", views.ContactUsForm.as_view(), name="contact-us"),
    path("products/<slug:tag>/", views.ProductListView.as_view(), name="products"),
    path(
        "product/<slug:slug>/", DetailView.as_view(model=models.Product), name="product"
    ),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html", form_class=forms.AuthenticationForm
        ),
        name="login",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
