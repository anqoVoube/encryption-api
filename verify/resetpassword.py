from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
from verify.serializers import ResetPasswordSerializer
from rest_framework import status
from django.db import connection

from .tasks import reset_password_email_confirmation
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    if request.method == "POST":
        serializer = ResetPasswordSerializer(data = request.data) #registration.queries + 1
        if serializer.is_valid():
            user = serializer.save()
            reset_password_email_confirmation.delay(user) #.delay
            message = "We've sent you email for further steps to reset the password."
            return Response({"success": [message]})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) #Overall queries for registration ("POST" method) = 3
