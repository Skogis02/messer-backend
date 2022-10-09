import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.utils import IntegrityError
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_out
from api.models import DefaultUser, Friendship, FriendRequest, Message
from api.serializers import MessageOutSerializer, FriendRequestOutSerializer, FriendshipOutSerializer
from .serializers import EndpointInSerializer, SendMessageSerializer, SendFriendRequestSerializer, \
    RespondToFriendRequestSerializer, RemoveFriendSerializer


def login_required(endpoint):
    def protected_endpoint(*args, **kwargs):
        self = args[0]
        assert type(self) == APIConsumer, TypeError("Missing arg 'self'!")
        if not self.scope['session'].exists(self.scope['session'].session_key):
            self.scope['session'].flush()
            self.send('Authentication Failed: Login Required!')
            return
        endpoint(*args, **kwargs)

    return protected_endpoint


class Endpoint:
    def __init__(self, endpoint: callable, serializer=None):
        self.endpoint = endpoint
        self.serializer = serializer

    def __call__(self, *args, **kwargs):
        return self.endpoint(*args, **kwargs)


class APIConsumer(WebsocketConsumer):
    """
        Requires the following endpoints:

        - Sending a message
        - Making a friend request
        - Respond to friend request
        - Remove a friend

        Future:

        - Reacting to a message
        - Searching for usernames
        - Login/Logout/Register

        A message is expected to have the following format:

        {
        endpoint: "<TYPE>",
        content: {<OBJECT>}
        }

    """

    def __init__(self):
        super().__init__(self)
        self.user = None
        self.endpoints = None
        self.request_count = None
        user_logged_out.connect(receiver=self.logout_callback)
        post_save.connect(receiver=self.received_message_callback, sender=Message)
        post_save.connect(receiver=self.received_friend_request_callback, sender=FriendRequest)
        post_save.connect(receiver=self.new_friend_callback, sender=Friendship)
        self.endpoints = {
            "send_message": Endpoint(endpoint=self.send_message,
                                     serializer=SendMessageSerializer),
            "send_friend_request": Endpoint(endpoint=self.send_friend_request,
                                            serializer=SendFriendRequestSerializer),
            "respond_to_friend_request": Endpoint(endpoint=self.respond_to_friend_request,
                                                  serializer=RespondToFriendRequestSerializer),
            'remove_friend': Endpoint(endpoint=self.remove_friend,
                                      serializer=RemoveFriendSerializer)
        }

    def connect(self):
        self.user = self.scope['user']
        if not (self.user and self.user.is_authenticated):
            self.close(code="Login required!")
            return
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            msg = json.loads(text_data)
        except json.JSONDecodeError as e:
            self.wrap_and_send('Response', {'Error': 'Invalid format!'})
            return
        serializer = EndpointInSerializer(data=msg, context={'consumer': self})
        if not serializer.is_valid():
            self.wrap_and_send('Response', serializer.errors)
            return
        endpoint, endpoint_serializer = serializer.validated_data['endpoint'], serializer.validated_data['content']
        endpoint(**endpoint_serializer.validated_data)

    # ENDPOINTS:

    def send_message(self, friendship, content):
        Message.objects.create(friendship=friendship, content=content)
        self.wrap_and_send('Response', {'Success': 'Message sent.'})

    def send_friend_request(self, friend_request):
        try:
            friend_request.save(force_insert=True)
        except IntegrityError as e:
            self.wrap_and_send('Response', {'Error': 'You have already sent a friend request to that user.'})
        except AssertionError as e:
            self.wrap_and_send('Response', {'Error': str(e)})

    def respond_to_friend_request(self, friend_request, accept):
        if accept:
            friend_request.accept_request()
            self.wrap_and_send('Response', {'Errors': '', 'status': 'Friend request accepted.'})
            return
        friend_request.reject_request()
        self.wrap_and_send('Response', {'Errors': '', 'status': 'Friend request rejected.'})

    def remove_friend(self, friendship):
        friendship.delete()
        self.wrap_and_send('Response', {'Errors': '', 'status': 'Friend removed.'})

    # CALLBACKS

    def logout_callback(self, sender, request, user, **kwargs):
        if not self.user == user:
            return
        self.send("Connection closing: Logging out.")
        async_to_sync(self.close())

    def received_message_callback(self, instance, created, **kwargs):
        if not (created and instance.friendship.friend == self.user):
            return
        serializer = MessageOutSerializer(instance)
        self.wrap_and_send(msg_type="received_message", content=serializer.data)

    def received_friend_request_callback(self, instance, created, **kwargs):
        if not (created and instance.to_user == self.user):
            return
        serializer = FriendRequestOutSerializer(instance)
        self.wrap_and_send(msg_type="new_friend_request", content=serializer.data)

    def new_friend_callback(self, instance, created, **kwargs):
        if not (created and instance.user == self.user):
            return
        serializer = FriendshipOutSerializer(instance)
        self.wrap_and_send(msg_type="new_friend", content=serializer.data)

    # UTILITIES

    def wrap_and_send(self, msg_type, content):
        data = {'type': msg_type,
                'content': content}
        self.send(json.dumps(data))










