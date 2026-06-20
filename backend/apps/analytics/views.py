# PATH: apps/analytics/views.py

from rest_framework import generics, permissions
from apps.stores.models import Store
from apps.users.permissions import IsAdmin
from .models import CustomerBehavior
from .serializers import CustomerBehaviorSerializer


class TrackBehaviorView(generics.CreateAPIView):
    """
    POST /api/v1/analytics/track/

    Called by the frontend (or AI tools) every time a customer does something
    meaningful — views a product, searches, adds to cart, etc.
    Open to everyone (even anonymous users) since tracking happens before login too.
    """
    serializer_class = CustomerBehaviorSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Always attach the single store, and the logged-in user if there is one.
        # Anonymous users are tracked through session_key instead (sent by frontend).
        store = Store.objects.first()
        serializer.save(
            store=store,
            user=self.request.user if self.request.user.is_authenticated else None,
        )


class CustomerBehaviorListView(generics.ListAPIView):
    """
    GET /api/v1/analytics/behavior/

    Admin-only — lets admin inspect raw behavior records, useful while
    building/debugging the recommendation engine later.
    Supports basic filtering: ?action=view&entity_type=product
    """
    serializer_class = CustomerBehaviorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = CustomerBehavior.objects.all()

        action = self.request.query_params.get('action')
        if action:
            qs = qs.filter(action=action)

        entity_type = self.request.query_params.get('entity_type')
        if entity_type:
            qs = qs.filter(entity_type=entity_type)

        return qs
