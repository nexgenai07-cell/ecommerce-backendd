# PATH: apps/products/discount_urls.py
# No changes needed for this ticket — routing already exposes
# DELETE /discounts/{id}/ (soft delete) and PUT /discounts/{id}/
# (restore via is_active=true) through the standard router actions.

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .discount_views import DiscountViewSet, DiscountValidateView

router = DefaultRouter()
router.register('', DiscountViewSet, basename='discount')

urlpatterns = [
    path('validate/', DiscountValidateView.as_view(), name='discount-validate'),
    path('', include(router.urls)),
]