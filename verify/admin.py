from django.contrib import admin
from .models import User, Client, Offers, Chat, BlockList
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Offers)
admin.site.register(Chat)
admin.site.register(BlockList)
# Register your models here.
