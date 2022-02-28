from time import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from datetime import datetime, timedelta
import uuid

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    delete_time = models.CharField(max_length=200, default = str(datetime.now() + timedelta(minutes = 1)))
    def save(self, *args, **kwargs):
       created = not self.pk
       super().save(*args, **kwargs)
       if created:
           url_for_photo = f'https://avatars.dicebear.com/api/initials/{self.first_name}-{self.last_name}.svg'
           Client.objects.create(first_name = self.first_name, last_name = self.last_name, user=self, photo_url=url_for_photo, slug=self.username) #registration.queries + 1

    def __str__(self):
        return str(self.username)
            

class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo_url = models.CharField(max_length=200, default='https://avatars.dicebear.com/api/initials/safety-esmsage.svg?backgroundColors[]=blue')
    friends = models.ManyToManyField('self')
    slug = models.SlugField(unique=True, primary_key=True)
    # def save(self, *args, **kwargs):
    #    created = not self.pk
    #    super().save(*args, **kwargs)
    #    if created:
    #        Searchfriend.objects.create(user_model = self, slug = self.slug)
    def __str__(self):
        return str(self.user)


# class Searchfriend(models.Model):
#     search_user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='search_user')
#     friend_offer = models.BooleanField(default=False)
#     slug = models.SlugField(unique=False, primary_key=True)

#     def __str__(self):
#         return str(self.search_user)

class Offers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    from_user = models.ForeignKey(Client, models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='to_user')

    def __str__(self):
        return str(self.id)

        
class Chat(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='user2')
    key = models.CharField(max_length = 100, null=False, blank=False)
    is_active = models.BooleanField(null=False, blank=False)
    time_to_activate = models.CharField(max_length=50, null=True, blank=True)
    output = models.TextField(max_length=500, null=True, blank=True)


class BlockList(models.Model):
    for_user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='block_for_user')
    which_user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='block_which_user')

    def __str__(self):
        return f'{self.for_user} banned {self.which_user}'
        
# from verify.models import User
# x = User(first_name="Jamoliddin", last_name="Bakhriddinov", username="anqov2", email="alex.person72@mail.ru", email_confirmed=True)
# x.set_password("anqov")
# x.save()