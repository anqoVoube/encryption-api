from .models import Offers, Client, BlockList
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def send_offer(request, slug, send):
    if request.method == "GET":
        if send == "send":
            if not BlockList.objects.filter(for_user__user__username = slug, which_user__user = request.user).exists():
                request_user = Client.objects.get(user=request.user)
                sending_offer_to_user = Client.objects.select_related('user').get(user__username=slug)
                if sending_offer_to_user.user.email_confirmed == True:
                    Offers.objects.get_or_create(from_user=request_user, to_user = sending_offer_to_user)
                    return Response({"success": ["Your offer was successfully sent."]})
            return Response({"failed": "You are blocked."})


    return Response({"error": ["Error occurred. Code: o_sx17. Please contact our team, so it won't happen again.)"]})