from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from verify.permissions import ChatPermission
from .models import Client, Offers, Chat
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from .serializers import ClientSerializer, CustomJWTSerializer, EncryptionSerializer, PasswordCheckerSerializer, OfferSerializer, SearchSerializer, ChatListSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework import status
from django.db import connection
from .tasks import key_generation, create_chat
from rest_framework import filters
from django.db.models import Q
from datetime import datetime, timedelta
from .permissions import ChatPermission
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()
class ActivateAccount(APIView):
    def get(self, request, uidb64, token, format=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.filter(pk=uid).values().first()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token) and user['email_confirmed'] == False:
            user['is_active'] = True
            user['email_confirmed'] = True
            save_user = User(**user)
            save_user.save()
            message = "Your account has been verified successfully!"
            return Response({"success": [message]})
        elif user['email_confirmed'] == True:
            message = "Your account already verified!"
            return Response({"error": [message]})
        else:
            message = 'Error occurred while verification of your email, possibly it was expired.'
            return Response({"error": [message]})


# Edit Profile View

# class ClientSelfView(RetrieveAPIView):
#     serializer_class = ClientSerializer
#     def get(self, request, *args, **kwargs):
#         try:
#             client_data = Client.objects.filter(user = self.request.user).values().first()
#             return Response(client_data)
#         except:
#             raise Http404
        


class ClientSelfView(ListAPIView):
    serializer_class = ClientSerializer
    def get_queryset(self):
        try:
            return Client.objects.filter(user = self.request.user).select_related('user')
        except Client.DoesNotExist or Client.MultipleObjectsReturned:
            raise Http404


class TokenObtainModifiedPairView(TokenViewBase):
    serializer_class = CustomJWTSerializer

class PassworResetView(APIView):
    def get_object(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.filter(pk=uid).values().first()
            if account_activation_token.check_token(user, token):
                x = User.objects.filter(username=str(user)).values().first()
                return x
            raise Http404
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, User.MultipleObjectsReturned):
            raise Http404

    def get(self, request, uidb64, token, format=None):
        data = self.get_object(uidb64, token)
        message = "You may now reset your password"
        return Response({"success": [message]})

    def post(self, request, uidb64, token):
        data = self.get_object(uidb64, token)
        serializer = PasswordCheckerSerializer(data, request.data)
        if serializer.is_valid():
            password = serializer.save()
            data.set_password(password)
            data.save()
            message = "The password was changed successfully"
            return Response({"success": [message]})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferAcceptionView(APIView):
    def get_object(self, uuid, acception):
        try:
            if acception:
                offer_object = Offers.objects.select_related('to_user').select_related('from_user').filter(id=str(uuid)).first()
                self.check_object_permissions(self.request, offer_object)
                return offer_object
            else:
                raise Http404
        except:
            raise Http404 
    
    def get(self, request, uuid, acception, format=None):
        data = self.get_object(uuid, acception)
        print(data)
        from_client_user = data.from_user
        to_client_user = data.to_user
        if acception % 2 == 0:
            from_client_user.friends.add(to_client_user)
            key = key_generation()
            Chat.objects.create(user1 = from_client_user, user2 = to_client_user, key=key, is_active=True)
            message = "Successfully added"
        else:
            message = "Successfully rejected"
        data.delete()
        return Response({"success": [message]})
    
class SearchList(ListAPIView):
    serializer_class = SearchSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']
    def get_queryset(self):
        return Client.objects.select_related('user').exclude(user=self.request.user).exclude(user__email_confirmed = False)
    
class OffersList(ListAPIView):
    serializer_class = OfferSerializer
    def get_queryset(self):
        return Offers.objects.filter(to_user__user=self.request.user)


class ChatsView(ListAPIView):
    serializer_class = ChatListSerializer
    def get_queryset(self):
        return Chat.objects.filter(Q(user1__user=self.request.user) | Q(user2__user = self.request.user))

class ChatSelfView(APIView):
    permission_classes = [ChatPermission]
    def get_object(self, uuid):
        try:
            obj = Chat.objects.get(id=uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except:
            raise Http404

    @swagger_auto_schema(operation_description="description", request_body=EncryptionSerializer)
    def patch(self, request, uuid):
        data = self.get_object(uuid)
        if data is None:
            raise Http404
        time_to_activate_the_chat = data.time_to_activate
        if data.is_active == 0 and str(time_to_activate_the_chat) > str(datetime.now()):
            time_left = time_left_function(time_to_activate_the_chat)
            return Response({"time-left": [time_left]})
        serializer = EncryptionSerializer(data, context={'request': request}, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseChatView(APIView):
    def get(self, request, uuid, activation):
        data = Chat.objects.get(id = uuid)
        if activation == 0:
            data.is_active = False
            data.time_to_activate = str(datetime.now() + timedelta(minutes = 5))
            data.save()
        else:

            if str(data.time_to_activate) > str(datetime.now()):
                time_left = time_left_function(data.time_to_activate)
                return Response({"time-left": [time_left]})
            else:
                data.is_active = True
                data.key = key_generation()
                data.save()
                message = "Restored"
                return Response({"success": [message]})
        message = "Chat was closed successfully. Now you should wait 5 minutes to open it again."
        return Response({"success": [message]})


def time_left_function(time_to_activate):
    get_time = str(time_to_activate)[:-7]
    filtering = '%Y-%m-%d %H:%M:%S'
    now_time = str(datetime.now())
    real_time_for_activating = datetime.strptime(get_time, filtering)
    current_time = datetime.strptime(now_time[:-7], filtering)
    time_left = str(real_time_for_activating - current_time)[2:]
    print(time_left)
    return time_left