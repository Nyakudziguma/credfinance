from django.urls import path
from django.contrib import admin
from. import views

urlpatterns = [
    path('webhook', views.WebhookView.as_view(), name='whatsapp-webhook'),
    path('faqs', views.faqs, name='faqs'),
]
