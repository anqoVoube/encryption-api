from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
from verify.serializers import UserSerializer
from rest_framework import status
from django.db import connection
from drf_yasg.utils import swagger_auto_schema

from .tasks import send_email_confirmation

@swagger_auto_schema(methods=['post'], request_body=UserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    
    if request.method == "POST":
        serializer = UserSerializer(data = request.data) #registration.queries + 1
        if serializer.is_valid():
            instance = serializer.save()
            user = serializer.data
            user['id'] = instance.id
            user['email_confirmed'] = False
            send_email_confirmation.delay(user) #.delay
            message = "Please Confirm your email to complete registration."
            return Response({"success": [message]})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) #Overall queries for registration ("POST" method) = 5
