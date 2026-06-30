# PATH: apps/users/twofactor_views.py
# This is a NEW file. Keep it separate from views.py to stay organized
# since 2FA has its own dedicated logic.
#
# Required pip installs:
#   pip install pyotp qrcode pillow

import pyotp
import qrcode
import io
import base64
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import TwoFactorAuth


class Enable2FAView(APIView):
    """
    POST /api/v1/auth/2fa/enable/

    Step 1 of 2FA setup. Generates a new TOTP secret and returns it as a
    QR code (base64 image) the user scans with Google Authenticator /
    Authy / Microsoft Authenticator etc.

    IMPORTANT: This does NOT turn on 2FA yet — is_enabled stays False
    until the user proves they scanned it correctly via Verify2FAView.
    This prevents someone from accidentally locking themselves out if
    the QR code never actually got scanned.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # Generate a new secret each time enable/ is called (overwrites any
        # previous un-confirmed attempt)
        secret = pyotp.random_base32()
        TwoFactorAuth.objects.update_or_create(
            user=user,
            defaults={'secret': secret, 'is_enabled': False}
        )

        # Build the otpauth:// URI that authenticator apps understand
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='AI Commerce Platform'
        )

        # Render as a QR code image, encode as base64 so the frontend can
        # display it directly in an <img src="data:image/png;base64,..."> tag
        qr_img = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'message': 'Scan this QR code with your authenticator app, then call /verify/ with a code.',
            'qr_code_base64': f'data:image/png;base64,{qr_base64}',
            'manual_entry_key': secret,  # shown as fallback if user can't scan
        }, status=status.HTTP_200_OK)


class Verify2FAView(APIView):
    """
    POST /api/v1/auth/2fa/verify/
    Request: { "otp": "123456" }

    Step 2 of setup — user enters the 6-digit code currently shown in their
    authenticator app. If it matches, 2FA is officially turned on.

    This same endpoint shape is also what LOGIN would call afterwards if
    2FA is enabled (check otp as a second step after password) — that
    login-flow wiring is a TODO once this base setup is confirmed working.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        otp = request.data.get('otp')
        if not otp:
            return Response({'error': 'otp is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {'error': 'No 2FA setup found. Call /2fa/enable/ first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(two_fa.secret)
        if not totp.verify(otp, valid_window=1):  # valid_window=1 allows ±30s clock drift
            return Response({'error': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)

        two_fa.is_enabled = True
        two_fa.save()

        return Response({'message': 'Two-factor authentication enabled successfully.'}, status=status.HTTP_200_OK)


class Disable2FAView(APIView):
    """
    POST /api/v1/auth/2fa/disable/
    Request: { "password": "string" }  — password required as confirmation,
    same security pattern as delete account.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        if not request.user.check_password(password or ''):
            return Response({'error': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

        TwoFactorAuth.objects.filter(user=request.user).delete()

        return Response({'message': 'Two-factor authentication disabled.'}, status=status.HTTP_200_OK)