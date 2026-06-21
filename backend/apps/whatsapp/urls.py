# PATH: apps/whatsapp/urls.py

from django.urls import path
from .views import WhatsAppWebhookView, SendWhatsAppMessageView

# mounted at /api/v1/whatsapp/ in core/urls.py
urlpatterns = [
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('send/', SendWhatsAppMessageView.as_view(), name='whatsapp-send'),
]