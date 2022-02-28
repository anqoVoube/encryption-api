from rest_framework.permissions import BasePermission

class ChatPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.user1.user == request.user) or (obj.user2.user == request.user)

class OfferPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.to_user == request.user