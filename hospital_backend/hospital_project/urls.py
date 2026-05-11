"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from hospital_app.views import test_ai_connection

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Toutes les URLs de l'application hospital_app
    path('', include('hospital_app.urls')),

    # Endpoint pour tester la connexion gRPC avec le service AI
    path("test-ai-grpc/", test_ai_connection, name="test_ai_connection"),
]
