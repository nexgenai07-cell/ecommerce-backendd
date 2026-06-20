"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# PATH: core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.cart.urls import wishlist_urlpatterns
from apps.orders.urls import admin_order_urlpatterns, return_urlpatterns, admin_return_urlpatterns, complaint_urlpatterns, admin_complaint_urlpatterns
from apps.ai.urls import audit_log_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Module 1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/stores/', include('apps.stores.urls')),

    # Module 2
    path('api/v1/categories/', include('apps.categories.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/discounts/', include('apps.products.discount_urls')),

    # Module 3 — Cart, Wishlist, Orders, Returns, Complaints
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/wishlist/', include((wishlist_urlpatterns, 'wishlist'))),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/admin/orders/', include((admin_order_urlpatterns, 'admin-orders'))),
    path('api/v1/returns/', include((return_urlpatterns, 'returns'))),
    path('api/v1/admin/returns/', include((admin_return_urlpatterns, 'admin-returns'))),
    path('api/v1/complaints/', include((complaint_urlpatterns, 'complaints'))),
    path('api/v1/admin/complaints/', include((admin_complaint_urlpatterns, 'admin-complaints'))),

    # Notifications
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # AI — chat sessions/messages + audit log
    path('api/v1/chat/', include('apps.ai.urls')),
    path('api/v1/admin/audit-logs/', include((audit_log_urlpatterns, 'audit-logs'))),

    # Analytics — customer behavior tracking
    path('api/v1/analytics/', include('apps.analytics.urls')),

    # Social — posts, accounts, analytics
    path('api/v1/social/', include('apps.social.urls')),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)