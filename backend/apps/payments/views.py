import stripe

from django.conf import settings

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_number = request.data.get("order_number")

        if not order_number:
            return Response(
                {"error": "order_number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(
                order_number=order_number,
                customer__user=request.user,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency="pkr",  # Change to "usd" if your Stripe account uses USD
                metadata={
                    "order_id": order.id,
                    "order_number": order.order_number,
                },
            )

            payment = order.payment
            payment.stripe_payment_intent_id = intent.id
            payment.save()

            return Response(
                {
                    "client_secret": intent.client_secret,
                    "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                    "amount": int(order.total_amount * 100),
                    "currency": "pkr",  # Must match the PaymentIntent currency
                    "order_number": order.order_number,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )