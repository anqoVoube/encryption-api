from rest_framework import serializers
from .models import Chat, Offers, User, Client, BlockList
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from email_validator import validate_email, EmailNotValidError
from django.db import connection
import string
import random
from django.conf import settings
from drf_yasg import openapi
from django.db.models import Q
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True
            }
        }

    def validate(self, attrs):
        print(attrs)
        username = attrs['username']
        email = attrs['email']
        password = attrs['password']
        password2 = attrs['password2']
        first_name = attrs['first_name']
        last_name = attrs['last_name']
        dictionary_errors = {}
        
        if str(username).find('@') != -1:
            message = 'You can\'t use symbol \'@\' in your username field'
            dictionary_errors['wrong-symbol'] = [message]

        if len(username) < 3:
            message = 'The length of your username must contain at least 3 letters.'
            dictionary_errors['username-length'] = [message]

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            dictionary_errors['invalid-email'] = [str(e)]


        if password != password2:
            message = "Passwords didn't match"
            dictionary_errors['password'] = [message]

        if len(first_name) <= 1 or str(first_name).isalpha() == False:
            message = "Please provide your real name, so the people could find you. This field must have only english letters."
            dictionary_errors['fname-error'] = [message]
        
        if len(last_name) <= 1 or str(last_name).isalpha() == False:
            message = "Please provide your real last name, so the people could find you. This field must have only english letters."
            dictionary_errors['lname-error'] = [message]

        if User.objects.filter(email = email).exists(): #registration.queries + 1
            message = 'This email is already taken'
            dictionary_errors['email'] = [message]
        
        if User.objects.filter(username = username).exists(): #registration.queries + 1
            message = 'This username is already taken'
            dictionary_errors['username'] = [message]

        if dictionary_errors:
            raise serializers.ValidationError(dictionary_errors)

        return attrs


    
    def save(self):
        validated_data = self.validated_data
        password = validated_data['password']
        password2 = validated_data['password2']
        email = validated_data['email']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        username = validated_data['username']
        
        user = User(first_name=first_name, last_name=last_name, email=email, username=username)
        user.set_password(password)
        user.save() #registration.queries + 1
        return user


class ClientSerializer(serializers.ModelSerializer):
    notifications = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = ['notifications', 'photo_url', 'friends', 'slug', 'first_name', 'last_name']

    def get_notifications(self, obj):
        return Offers.objects.filter(to_user = obj).count()

class CustomJWTSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }
        try:
            user = User.objects.get(username=attrs.get("username"))
            email_confirmed = user.email_confirmed
        except User.DoesNotExist:
            user = None
            email_confirmed = None
         #I changed here a little bit
        if email_confirmed and user:
            credentials['username'] = user.username
            return super().validate(credentials)
        elif user and not email_confirmed:
            message = "Email is not verified"
            return {"error": [message]}
        else:
            message = "No active account found with the given credentials"
            return {"detail": [message]}

        #User -> pass
        #Client user=User, email_confirmed = boolean

# ---------------------------
class ResetPasswordSerializer(serializers.ModelSerializer):
    typed_string = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['typed_string']
    def save(self): 
        validated_data = self.validated_data
        typed_string = validated_data['typed_string']
        if str(typed_string).find('@') != -1:
            if User.objects.filter(email = typed_string).exists(): #registration.queries + 1
                try:
                    return User.objects.filter(email = typed_string).values().first() #registration.queries + 1
                except:
                    message = "Some error occurred while resetting your password. Please, try later."
                    raise serializers.ValidationError({"error": [message]}) 

        else:
            if User.objects.filter(username = typed_string).exists(): #registration.queries + 1
                try:
                    return User.objects.filter(username = typed_string).values().first() #registration.queries + 1
                except User.MultipleObjectsReturned:
                    message = "Some error occurred while resetting your password. Please, try later."
                    raise serializers.ValidationError({"error": [message]}) 
            else:
                message = ["There is no user with that username or email!"]
                raise serializers.ValidationError({"error": [message]})

class PasswordCheckerSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['password1', 'password2']
    
    def save(self):
        validated_data = self.validated_data
        password1 = validated_data['password1']
        password2 = validated_data['password2']
        if password1 != password2:
            message = "Passwords didn't match"
            raise serializers.ValidationError({"error": [message]})
        return password1


class SearchSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    offer_send_url = serializers.SerializerMethodField(allow_null=True)
    is_your_friend = serializers.SerializerMethodField()
    friend_offer = serializers.SerializerMethodField()
    block_user = serializers.SerializerMethodField()
    some_thing = False  #
    friends_list = [] # BY THIS WE ARE REDUCING THE OVERALL QUERY. FOR INSTANCE, WE WILL HIT THE DB 2*N times
    sended_offers = [] # where N is number of offers, if we will query the same query(defining the instance of current logged in user 'line 170')
    count_of_sended_offers = 0 #
    class Meta:
        model = Client
        fields = ['user', 'offer_send_url', 'friend_offer', 'is_your_friend', 'block_user'] # , 'offer_send_url', 'friend_offer', 'is_your_friend'
        read_only_fields = ['search_user', 'offer_send_url', 'is_your_friend', 'block_user'] # , 'offer_send_url', 'is_your_friend'
    
    def get_is_your_friend(self, obj):
        print("187")
        if self.some_thing == False:
            try:
                user_data = self.context['request'].user
                client_user = Client.objects.prefetch_related('friends').get(user = user_data)
                self.some_thing = client_user
            except:
                raise serializers.ValidationError({"error": ["Error occurred. Code: sx191. Please contact our team, so it won't happen again."]})
        else:
            client_user = self.some_thing
        if self.friends_list == []:
            query_of_friends = client_user.friends.all().values('slug')
            for i in query_of_friends:
                self.friends_list.append(str(i['slug']))
        if str(obj.user) in self.friends_list: #better str(obj.user) or obj.user.username?
            return True
        if BlockList.objects.filter(for_user = obj, which_user = client_user).exists():
            return "You are blocked"
        print("205")
        return False



    def get_friend_offer(self, obj):
        print("211")
        if self.count_of_sended_offers == 0:
            self.count_of_sended_offers += 1
            if self.sended_offers == []:
                try:
                    filtering_sended_offers = Offers.objects.filter(from_user__user = self.context['request'].user).values('to_user')
                    for i in filtering_sended_offers:
                        self.sended_offers.append(str(i['to_user']))
                except:
                    raise serializers.ValidationError({"error": ["Error occurred. Code: sx213. Please contact our team, so it won't happen again."]})
        if self.sended_offers != [] and (obj.user in self.sended_offers):
            if self.is_your_friend != True:
                return True
            else:
                return None
        print("226")
        return False

    
    def get_offer_send_url(self, obj):
        print("231")
        client_object = Client.objects.get(user = self.context['request'].user)
        if BlockList.objects.filter(for_user = obj, which_user = client_object).exists():
            return None
        if self.get_is_your_friend(obj):
            return True
        print("236")
        return str(f'{settings.DOMAIN}/searchfriend/{obj.user}/send/')

    def get_block_user(self, obj):
        print("240")
        if BlockList.objects.filter(for_user__user = self.context['request'].user, which_user = obj).exists():
            return True
        print("243")
        return str(f'{settings.DOMAIN}/block/{obj.user}/')


# str(f'{settings.DOMAIN}/searchfriend/{obj.user}/send/')

class OfferSerializer(serializers.ModelSerializer):
    acception_url = serializers.SerializerMethodField()
    decline_url = serializers.SerializerMethodField()
    class Meta:
        model = Offers
        fields = ['from_user', 'acception_url', 'decline_url']
        read_only_fields = ['from_user', 'acception_url']

    def get_acception_url(self, obj):
        random_number = int(random.randrange(2, 1000, 2))
        return str(f'{settings.DOMAIN}/offers/{obj.id}/{random_number}/')

    def get_decline_url(self, obj):
        random_number = int(random.randrange(1, 1000, 2))
        return str(f'{settings.DOMAIN}/offers/{obj.id}/{random_number}/')

class EncryptionSerializer(serializers.ModelSerializer):
    message = serializers.CharField(default="Nothing")
    encrypt_or_decrypt = serializers.BooleanField(default=True, help_text='Encrypt = True, Decrypt = False')
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "Email",
            "properties": {
                "message": openapi.Schema(
                    title="Message",
                    type=openapi.TYPE_STRING,
                ),
                "encrypt_or_decrypt": openapi.Schema(
                    title="Encrypt or decrypt the message",
                    type=openapi.TYPE_BOOLEAN,
                ),
            },
            "required": ["message", "encrypt_or_decrypt"],
         }
        model = Chat
        fields = ['message', 'encrypt_or_decrypt', 'output']
        read_only_fields = ['output']

    def update(self, instance, validated_data):
        get_message = validated_data.get('message', '')
        encrypt_or_decrypt = validated_data.get('encrypt_or_decrypt', True)
        if encrypt_or_decrypt:
            try:
                encrypted_message = encryption(get_message, str(instance.key))
                instance.output = encrypted_message
            except:
                message = "Error occurred while encrypting your message. Please, try again."
                raise serializers.ValidationError({"error": [message]})
            return instance
        try:
            decrypted_message = decryption(get_message, str(instance.key))
            instance.output = decrypted_message
        except:
            message = "Error occurred while decrypting your message. Please, try again."
            raise serializers.ValidationError({"error": [message]})
        
        return instance



class ChatListSerializer(serializers.ModelSerializer):
    chat_with = serializers.SerializerMethodField()
    chat_url = serializers.SerializerMethodField()
    class Meta:
        model = Chat
        fields = ['chat_url', 'chat_with']
        read_only_fields = ['chat_with']
    
    def get_chat_with(self, obj):
        current_client_user = Client.objects.get(user = self.context['request'].user)
        if obj.user1 == current_client_user:
            return f'{str(obj.user2)} | {obj.user2.first_name} {obj.user2.last_name}'
        return f'{str(obj.user1)} | {obj.user1.first_name} {obj.user1.last_name}'

    def get_chat_url(self, obj):
        return str(f'{settings.DOMAIN}/chats/{obj.id}/')




class CloseChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['is_active', 'time_to_activate']
        read_only_fields = ['time_to_activate']



simple = string.ascii_letters + string.digits + string.punctuation + " "
def encryption(message, key):
    if len(message) < 3: #Otherwise program won't work, because of slice method. It needs at least 3 letters.
        error_message = "Your message should contain at least 3 letters,"
        raise serializers.ValidationError({"error": [error_message]})

    is_reverse = random.randint(0, 1)
    keygen = ''
    if is_reverse == 1:
        message = message[::-1]
        keygen += "1"
    else:
        keygen += "0"
    is_reverse = random.randint(0, 1)
    if is_reverse == 1:
        key = key[::-1]
        keygen += "1-"
    else:
        keygen += "0-"
    for i in range(10):
        first_shuffle_integer = 0
        second_shuffle_integer = 0
        while first_shuffle_integer == second_shuffle_integer or first_shuffle_integer == 45 or second_shuffle_integer == 45:
            first_shuffle_integer = random.randint(30, 70)
            second_shuffle_integer = random.randint(20, 80)
        first_integer = max(first_shuffle_integer, second_shuffle_integer)
        second_integer = min(first_shuffle_integer, second_shuffle_integer)
        keygen += str(first_shuffle_integer) + "-"
        keygen += str(second_shuffle_integer) + "-"
        key = key[second_integer:first_integer] + key[:second_integer] + key[first_integer:]
    for i in range(0, len(keygen), 3):
        suske = random.randint(1, 50)
        if suske == 2:
            keygen = keygen[:i] + "45-" + keygen[i:]
    keygen = keygen[:len(keygen) - 1]
    first_maketrans = message.maketrans(simple, key)
    final_encrypted_text = message.translate(first_maketrans)
    first_letter_of_message = final_encrypted_text[0]
    return final_encrypted_text + first_letter_of_message + first_letter_of_message + keygen

def decryption(message, key):
    special_key = message[int(message.find(str(message[0]) + str(message[0])) + 2):]
    word_itself = str(message[:int(message.find(str(message[0]) + str(message[0]))):])
    if special_key[1] != "0":
        encrypted = key[::-1] 
    else:
        encrypted = key
    if special_key[0] != "0":
        message = message[::-1]
        word_itself = word_itself[::-1]
    listing = special_key[3:].split("-")
    while '45' in listing:
        listing.remove('45')
    for i in range(0, len(listing) - 1, 2):
        figure_1 = int(listing[i])
        figure_2 = int(listing[i + 1])
        if figure_1 > figure_2:
            listing[i], listing[i + 1] = figure_2,  figure_1
        figure_1 = int(listing[i])
        figure_2 = int(listing[i + 1])
        encrypted = encrypted[figure_1:figure_2] + encrypted[:figure_1] + encrypted[figure_2:]
    first_maketrans_1 = word_itself.maketrans(encrypted, simple)
    final_encrypted_text_1 = word_itself.translate(first_maketrans_1)
    return final_encrypted_text_1


