# PATH: apps/stores/urls.py

from django.urls import path
from .views import MyStoreView

urlpatterns = [
    path('me/', MyStoreView.as_view(), name='my-store'),
]