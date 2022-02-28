from django.urls import path
from .registration import registration
from .resetpassword import reset_password
from .views import ActivateAccount, PassworResetView, ClientSelfView, ChatSelfView, ChatsView, OfferAcceptionView, OffersList, SearchList, CloseChatView
from .offer_sender import send_offer
from .block_user import block_user
urlpatterns = [
    path('registration/', registration, name='registration'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('reset/<uidb64>/<token>/', PassworResetView.as_view(), name='permission-reset'),
    path('reset/', reset_password, name='reset-passowrd'),
    path('account/', ClientSelfView.as_view(), name='client-view'),
    path('offers/<uuid:uuid>/<int:acception>/', OfferAcceptionView.as_view(), name='offer-acception'),
    path('offers/', OffersList.as_view(), name='offers-list'),
    path('searchfriend/', SearchList.as_view(), name='search-list'),
    path('searchfriend/<slug:slug>/<send>/', send_offer, name='send-offer'),
    path('block/<slug:slug>/', block_user, name='block-user'),
    path('chats/', ChatsView.as_view(), name="chat-list"),
    path('chats/<uuid:uuid>/', ChatSelfView.as_view(), name="chat-detail"),
    path('chats/<uuid:uuid>/<int:activation>/', CloseChatView.as_view(), name="close-chat")
]
