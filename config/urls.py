"""
URL configuration for the unified Cardiovascular Risk Stratification project.

The `urlpatterns` list routes URLs to views.
See: https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Import your home view
from accounts.views import home  # Adjust this if home_view is elsewhere

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🔹 Home page
    path("", home, name="home"),

    # 🔹 App-level URL configs
    path("accounts/", include("accounts.urls")),  # Your app's routes
    #path("", include("cardiovascular_app.urls")),  # Mohammed’s app routes

    # 🔹 Authentication
    #path("login/", auth_views.LoginView.as_view(template_name="cardiovascular_app/login.html"), name="login"),
    path("login/", auth_views.LoginView.as_view(template_name="templates/users/login.html"), name="login")
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
