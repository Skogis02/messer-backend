import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_out
from api.models import Message, FriendRequest, Friendship
from api.serializers import MessageOutSerializer, FriendRequestOutSerializer, FriendshipOutSerializer
from .dataclasses_ import Error, Response
from .serializers import WsMessageSerializer, SendMessageSerializer, SendFriendRequestSerializer, RespondToFriendRequestSerializer

class APIConsumer(WebsocketConsumer):

    def __init__(self):
        super().__init__(self)
        self.user = None
        user_logged_out.connect(receiver=self.logout_callback)
        post_save.connect(receiver=self.received_message_callback, sender=Message)
        post_save.connect(receiver=self.received_friend_request_callback, sender=FriendRequest)
        post_save.connect(receiver=self.new_friend_callback, sender=Friendship)
        post_delete.connect(receiver=self.removed_friend_callback, sender=Friendship)
        self.endpoints = {endpoint: getattr(self, endpoint + '_endpoint') for endpoint in ENDPOINT_LIST}

    def connect(self):
        self.user = self.scope['user']
        if not (self.user and self.user.is_authenticated):
            self.close(code="Login required!")
            return
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            parsed_data = json.loads(text_data)
        except json.JSONDecodeError as e:
            self.respond(errors=[Error(
                'Invalid JSON Format.',
                code=0
            )])
            return
        serializer = WsMessageSerializer(data=parsed_data, endpoints=ENDPOINT_LIST)
        if not serializer.is_valid():
            self.respond(errors=[Error(
                'Serialization Error',
                code=1
            )])
            return
        endpoint_str = serializer.data['endpoint']
        assert endpoint_str in self.endpoints, AssertionError('Invalid endpoint from serializer.')
        self.endpoints[endpoint_str](serializer.data)

    # ENDPOINTS:

    def send_message_endpoint(self, data):
        serializer = SendMessageSerializer(data=data['content'])
        if not serializer.is_valid():
            self.respond('send_message', data['id'], errors=[Error('Serialization Error', code=11)])
            return
        friendship_queryset = self.user.friendships.filter(friend__username=serializer.data['friend'])
        if not friendship_queryset.exists():
            self.respond('send_message', data['id'], errors=[Error('User not in friend list.', code=12)])
            return
        Message.objects.create(friendship=friendship_queryset.first(), content=serializer.data['content'])
        self.respond('send_message,', data['id'], 'Message sent.')

    def send_friend_request_endpoint(self, data):
        serializer = SendFriendRequestSerializer(data=data['content'])
        if not serializer.is_valid():
            self.respond('send_friend_request', data['id'], errors=[Error('Serialization Error', code=21)])
            return

    def respond_to_friend_request_endpoint(self, data):
        pass

    def remove_friend_endpoint(self, data):
        pass

    def withdraw_friend_request_endpoint(self, data):
        pass

    def get_messages_endpoint(self, data):
        pass

    def get_friend_requests_endpoint(self, data):
        pass

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

    def removed_friend_callback(self, instance, **kwargs):
        if not instance.user == self.user:
            return
        serializer = FriendshipOutSerializer(instance)
        self.wrap_and_send(msg_type='removed_friend', content=serializer.data)

    # UTILITIES

    def wrap_and_send(self, msg_type, content):
        data = {'type': msg_type,
                'content': content}
        self.send(json.dumps(data))

    def respond(
        self,
        endpoint: str = '',
        id: int = 0,
        content: dict = {},
        errors: list = []
    ):
        self.send(json.dumps(
            Response(
                endpoint,
                id,
                content,
                errors
            ).as_dict()
        ))


ENDPOINT_LIST = [method.removesuffix('_endpoint') for method in dir(APIConsumer) \
    if not method.startswith('__') and method.endswith('_endpoint')]
