import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_out
from api.models import DefaultUser, Friendship, FriendRequest, Message
from api.serializers import MessageOutSerializer, FriendRequestOutSerializer


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


class APIConsumer(WebsocketConsumer):
    """
        Requires the following endpoints:

        - Sending a message
        - Making a friends request

        Future:

        - Reacting to a message
        - Searching for usernames
        - Login/Logout/Register

        A message is expected to have the following format:

        {
        type: "<TYPE>",
        value: {<OBJECT>}
        }

        """

    def __init__(self):
        super().__init__(self)
        self.user = None
        self.endpoints = {
            "send_message": self.send_message,
            "send_friend_request": self.send_friend_request,
        }
        user_logged_out.connect(receiver=self.logout_callback)
        post_save.connect(receiver=self.received_message_callback, sender=Message)
        post_save.connect(receiver=self.received_friend_request_callback, sender=FriendRequest)

    def connect(self):
        self.user = self.scope['user']
        print(self.user)
        if not (self.user and self.user.is_authenticated):
            self.close(code="Login required!")
            return
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            msg = json.loads(text_data)
        except json.JSONDecodeError as e:
            print(e)
            self.send("Invalid format.")
            return
        if 'endpoint' not in msg:
            self.send("Missing key 'endpoint'.")
            return
        elif 'data' not in msg:
            self.send("Missing key 'data''.")
            return
        msg_endpoint, msg_data = msg['endpoint'], msg['data']
        if msg_endpoint not in self.endpoints:
            self.send("'Invalid endpoint.")
            return
        endpoint = self.endpoints[msg_endpoint]
        endpoint(msg_data)
        return

    # ENDPOINTS:

    def send_message(self, data):

        """
        Required fields:
        -'friend'
        -'content'
        """

        if 'friend' not in data:
            self.send("Object 'data' missing key 'friend'.")
            return
        elif 'content' not in data:
            self.send("Object 'data' missing key 'content'.")
            return
        friend_username = data['friend']
        friend_queryset = self.user.friends.filter(username=friend_username)
        if not friend_queryset.exists():
            self.send("The provided user is not in your friends list.")
        friend = friend_queryset.first()
        friendship = self.user.friendships.filter(friend=friend).first()
        Message.objects.create(friendship=friendship, content=data['content'])
        self.send('Message sent!')

    def send_friend_request(self, data):

        """
        Required fields:
        -'to_user'
        """

        if 'to_user' not in data:
            self.send("Object 'data' missing key 'to_user'.")
            return
        to_username = data['to_user']
        to_user_queryset = DefaultUser.objects.filter(username=to_username)
        if not to_user_queryset.exists():
            self.send('That user could not be found!')
        to_user = to_user_queryset.first()
        try:
            FriendRequest.objects.create(from_user=self.user, to_user=to_user)
            self.send('Message sent!')
        except AssertionError as e:
            self.send('That user is already in your friends list!')

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
        self.wrap_and_send(title="new_message", content=serializer.data)

    def received_friend_request_callback(self, instance, created, **kwargs):
        if not (created and instance.to_user == self.user):
            return
        serializer = FriendRequestOutSerializer(instance)
        self.wrap_and_send(title="new_friend_request", content=serializer.data)

    # UTILITIES

    def wrap_and_send(self, title, content):
        data = {'title': title,
                'content': content}
        self.send(json.dumps(data))









