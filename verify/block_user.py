from .models import Client, Chat, BlockList
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def block_user(request, slug):
    if request.method == "GET":
        for_user = Client.objects.prefetch_related('friends').select_related('user').get(user=request.user)
        which_user = Client.objects.select_related('user').get(user__username=slug)
        
        if Chat.objects.filter(Q(user1 = for_user, user2 = which_user) | Q(user1 = which_user, user2 = for_user)).exists():
            try:
                delete_chat = Chat.objects.get(user1 = for_user, user2 = which_user)

            except Chat.DoesNotExist:
                delete_chat = Chat.objects.get(user1 = which_user, user2 = for_user)

            delete_chat.delete()

        if which_user in for_user.friends.all():
            for_user.friends.remove(which_user)
        BlockList.objects.get_or_create(for_user = for_user, which_user = which_user)
        return Response({"success": "Successfully blocked."})