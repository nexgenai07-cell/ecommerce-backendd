# PATH: apps/notifications/views.py

from django.db.models import Q
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer
from apps.users.permissions import IsAdmin
from apps.stores.models import Store


class NotificationViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    GET /api/v1/notifications/           -> list current user's notifications
    GET /api/v1/notifications/{id}/      -> retrieve a single notification
    PUT /api/v1/notifications/{id}/read/ -> mark as read
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Each user only ever sees their own notifications (or broadcast ones, user=null)
        return Notification.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )

    @action(detail=True, methods=['put'], url_path='read')
    def mark_read(self, request, pk=None):
        """PUT /api/v1/notifications/{id}/read/"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class SendNotificationView(APIView):
    """
    POST /api/v1/notifications/send/

    Admin-only endpoint to manually create/send a notification (e.g. broadcast
    announcements). This is also the same shape used internally by Celery tasks
    when triggering automatic notifications (order confirm/shipped/delivered,
    low stock alerts) — those call Notification.objects.create() directly in
    code, this endpoint is the equivalent for manual/admin-triggered sends.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        user_id = request.data.get('user')  # null/omitted = broadcast to all
        title = request.data.get('title')
        message = request.data.get('message')
        notif_type = request.data.get('type', 'general')
        sent_via = request.data.get('sent_via', 'web')

        if not title or not message:
            return Response(
                {'error': 'title and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = Notification.objects.create(
            store=Store.objects.first(),
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            sent_via=sent_via,
        )

        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)