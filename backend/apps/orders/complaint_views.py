# PATH: apps/orders/complaint_views.py
# (placed in apps/orders for URL convenience; imports the Complaint model from apps.returns)

from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.returns.models import Complaint
from apps.returns.complaint_serializers import (
    ComplaintSerializer, CreateComplaintSerializer,
    AdminComplaintStatusSerializer, AdminComplaintRespondSerializer,
)
from .models import Order, Customer
from apps.users.permissions import IsAdmin


class CreateComplaintView(generics.ListCreateAPIView):
    """
    POST /api/v1/complaints/ -> submit a complaint
    GET  /api/v1/complaints/ -> customer sees own, admin sees all
    """
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Complaint.objects.all().order_by('-created_at')
        return Complaint.objects.filter(customer__user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = CreateComplaintSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({'error': 'No customer profile found. Place an order first.'}, status=status.HTTP_400_BAD_REQUEST)

        order = None
        if data.get('order'):
            order = Order.objects.filter(id=data['order'], customer__user=request.user).first()

        complaint = Complaint.objects.create(
            customer=customer,
            order=order,
            type=data['type'],
            message=data['message'],
            status='open',
        )

        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)


class ComplaintDetailView(generics.RetrieveAPIView):
    """GET /api/v1/complaints/{id}/"""
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Complaint.objects.all()
        return Complaint.objects.filter(customer__user=user)


class AdminComplaintStatusUpdateView(APIView):
    """PUT /api/v1/admin/complaints/{id}/status/"""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            complaint = Complaint.objects.get(id=pk)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminComplaintStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complaint.status = serializer.validated_data['status']
        complaint.save()

        return Response(ComplaintSerializer(complaint).data)


class AdminComplaintRespondView(APIView):
    """PUT /api/v1/admin/complaints/{id}/respond/"""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            complaint = Complaint.objects.get(id=pk)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminComplaintRespondSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complaint.response = serializer.validated_data['response']
        complaint.resolved_by = request.user
        complaint.status = 'resolved'
        complaint.save()

        # TODO (BE2): trigger Celery task -> notify_customer_complaint_response.delay(complaint.id)

        return Response(ComplaintSerializer(complaint).data)