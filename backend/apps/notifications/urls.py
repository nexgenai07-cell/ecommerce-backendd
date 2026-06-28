# PATH: apps/notifications/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, SendNotificationView

router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')

urlpatterns = [
    path('send/', SendNotificationView.as_view(), name='notification-send'),
    path('', include(router.urls)),
]