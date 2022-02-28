from celery import shared_task
from django.template.loader import render_to_string 
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .models import Chat
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from verify.tokens import account_activation_token
from django.core.mail import EmailMessage
from datetime import datetime
import string
import random
@shared_task
def send_email_confirmation(user):
    message = render_to_string('account_activation_email.html', {
        'user': user['username'],
        'domain': '127.0.0.1:8000',
        'uid': urlsafe_base64_encode(force_bytes(user['id'])),
        'token': account_activation_token.make_token(user),
    })
    sms_message = EmailMessage("Safety Esmsage account confirmation", message, "safetyesmsage@gmail.com", [user['email']]) 
    sms_message.content_subtype = 'html' 
    sms_message.send()

@shared_task
def reset_password_email_confirmation(user):
    message = render_to_string('password_reset_email.html', {
        'user': user['username'],
        'domain': '127.0.0.1:8000',
        'uid': urlsafe_base64_encode(force_bytes(user['id'])),
        'token': account_activation_token.make_token(user),
    })
    sms_message = EmailMessage("Safety Esmsage password reset", message, "safetyesmsage@gmail.com", [user['email']]) 
    sms_message.content_subtype = 'html' 
    sms_message.send()

@shared_task
def user_delete():
    delete_user = User.objects.filter(email_confirmed = False, delete_time__lte = datetime.now())
    delete_user.delete()

@shared_task
def create_chat(user1, user2):
    user1.friends.add(user2)
    key = key_generation()
    Chat.objects.create(user1 = user1, user2 = user2, key=key, is_active=True)

def key_generation() -> str:
    simple = string.ascii_letters + string.digits + string.punctuation + " "
    simple = simple.replace('"', "•")
    a = [i for i in simple]
    random.shuffle(a)
    a = ''.join(a)
    return str(a)
