# PATH: apps/social/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SocialPostViewSet, SocialAccountViewSet, SocialPostAnalyticsView

# Router handles: list, retrieve, update, destroy + the @action endpoints
# (approve, reject, schedule, calendar) automatically
post_router = DefaultRouter()
post_router.register('posts', SocialPostViewSet, basename='social-post')

urlpatterns = [
    # extra explicit path to match the documented POST /posts/create/ spec
    path('posts/create/', SocialPostViewSet.as_view({'post': 'create'}), name='social-post-create'),
    path('analytics/<int:post_id>/', SocialPostAnalyticsView.as_view(), name='social-post-analytics'),

    # explicit connect endpoint — matches planning doc: POST /api/v1/social/accounts/connect/
    path('accounts/connect/', SocialAccountViewSet.as_view({'post': 'create'}), name='social-account-connect'),
    path('accounts/', SocialAccountViewSet.as_view({'get': 'list'}), name='social-account-list'),
]

urlpatterns += post_router.urls