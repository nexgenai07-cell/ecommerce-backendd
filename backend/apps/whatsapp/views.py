# PATH: apps/whatsapp/views.py

import os
import hmac
import hashlib
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import WhatsAppLog, WhatsAppSession
from .serializers import WhatsAppLogSerializer, WhatsAppSessionSerializer, SendWhatsAppMessageSerializer
from apps.users.permissions import IsAdmin
from apps.stores.models import Store

META_VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN', '')
META_WHATSAPP_TOKEN = os.getenv('META_WHATSAPP_TOKEN', '')
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID', '')
META_APP_SECRET = os.getenv('META_APP_SECRET', '')

# Registered admin numbers — in a real setup this should come from a DB table
# (e.g. a list on the Store model) rather than the .env file. Kept simple here.
ADMIN_PHONE_NUMBERS = [n.strip() for n in os.getenv('ADMIN_WHATSAPP_NUMBERS', '').split(',') if n.strip()]


def verify_meta_signature(request):
    """
    Verifies the X-Hub-Signature-256 header Meta sends with every webhook
    POST, proving the request really came from Meta and wasn't forged.
    """
    if not META_APP_SECRET:
        return True  # skip verification if not configured yet (dev mode)

    signature = request.headers.get('X-Hub-Signature-256', '')
    if not signature.startswith('sha256='):
        return False

    expected = hmac.new(
        META_APP_SECRET.encode(), request.body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature.split('sha256=')[-1], expected)


class WhatsAppWebhookView(APIView):
    """
    GET  /api/v1/whatsapp/webhook/  -> Meta's one-time verification handshake
    POST /api/v1/whatsapp/webhook/  -> incoming WhatsApp messages

    This is BE1's responsibility: receive, verify, log, and route the message.
    The actual conversation logic (multi-turn flows, tool calls, AI replies)
    lives in BE2's admin_agent.py / customer_wa_agent.py — see the
    route_to_ai_agent() placeholder below for the hand-off point.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Meta does not send our JWT — must stay open

    def get(self, request):
        """Meta calls this once when you set up the webhook in the Meta dashboard."""
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        if mode == 'subscribe' and token == META_VERIFY_TOKEN:
            return Response(int(challenge), status=status.HTTP_200_OK)

        return Response({'error': 'Verification failed.'}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        if not verify_meta_signature(request):
            return Response({'error': 'Invalid signature.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        try:
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            messages = value.get('messages')

            if not messages:
                # Could be a status update (delivered/read) rather than a message
                return Response(status=status.HTTP_200_OK)

            message_data = messages[0]
            phone_number = message_data['from']
            message_text = message_data.get('text', {}).get('body', '')

        except (KeyError, IndexError):
            # Malformed payload — log nothing, just acknowledge so Meta stops retrying
            return Response(status=status.HTTP_200_OK)

        is_admin = phone_number in ADMIN_PHONE_NUMBERS
        store = Store.objects.first()

        WhatsAppLog.objects.create(
            store=store,
            phone_number=phone_number,
            direction='inbound',
            message=message_text,
            is_admin=is_admin,
            metadata=data,
        )

        # Hand off to the AI agent (BE2). Must respond 200 to Meta quickly —
        # in production this should be pushed to a Celery/Redis queue instead
        # of processed synchronously here.
        self.route_to_ai_agent(phone_number, message_text, is_admin)

        return Response(status=status.HTTP_200_OK)

    def route_to_ai_agent(self, phone_number, message_text, is_admin):
        """
        TODO (BE2): Replace with the real routing call, e.g.:

            from ai_service.whatsapp.admin_bot import handle_admin_message
            from ai_service.whatsapp.customer_bot import handle_customer_message

            if is_admin:
                handle_admin_message.delay(phone_number, message_text)
            else:
                handle_customer_message.delay(phone_number, message_text)

        For now this is a no-op placeholder so the webhook endpoint itself
        is fully testable (via Meta's test console or curl) before the AI
        layer exists.
        """
        pass


class SendWhatsAppMessageView(APIView):
    """
    POST /api/v1/whatsapp/send/

    Sends an outbound WhatsApp message via the Meta Cloud API.
    Used both for manual admin sends and internally by Celery tasks
    (order confirmations, shipping updates, etc.) — anything that needs
    to push a WhatsApp message calls this same function.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = SendWhatsAppMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        message = serializer.validated_data['message']

        success, error = send_whatsapp_message(phone_number, message)

        if not success:
            return Response({'error': error}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'message': 'Sent successfully.'}, status=status.HTTP_200_OK)


def send_whatsapp_message(phone_number, message):
    """
    Shared helper — also called directly from Celery tasks (not just this view).
    Returns (success: bool, error: str | None).
    """
    if not META_WHATSAPP_TOKEN or not META_PHONE_NUMBER_ID:
        return False, 'WhatsApp credentials are not configured yet.'

    url = f'https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages'
    headers = {'Authorization': f'Bearer {META_WHATSAPP_TOKEN}'}
    payload = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
        'type': 'text',
        'text': {'body': message},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return False, str(e)

    store = Store.objects.first()
    WhatsAppLog.objects.create(
        store=store, phone_number=phone_number, direction='outbound',
        message=message, is_admin=phone_number in ADMIN_PHONE_NUMBERS,
    )

    return True, None


class AdminWhatsAppLogsView(generics.ListAPIView):
    """GET /api/v1/admin/whatsapp/logs/?phone_number="""
    serializer_class = WhatsAppLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = WhatsAppLog.objects.all()
        phone = self.request.query_params.get('phone_number')
        if phone:
            qs = qs.filter(phone_number=phone)
        return qs


class AdminWhatsAppSessionsView(generics.ListAPIView):
    """GET /api/v1/admin/whatsapp/sessions/"""
    serializer_class = WhatsAppSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = WhatsAppSession.objects.all().order_by('-last_active')