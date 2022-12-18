from rest_framework import serializers
from .models import DefaultUser, Message, FriendRequest, Friendship
from django.contrib.auth.hashers import make_password


class DefaultUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_password(data):
        return make_password(data)


class DefaultLoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class MessageOutSerializer(serializers.ModelSerializer):
    from_user = serializers.CharField(source='friendship.user')
    to_user = serializers.CharField(source='friendship.friend')

    class Meta:
        model = Message
        fields = ['from_user', 'to_user', 'created_at', 'has_been_read', 'read_at', 'content']


class FriendRequestOutSerializer(serializers.ModelSerializer):
    from_user = serializers.CharField(source='from_user.username')
    to_user = serializers.CharField(source='to_user.username')

    class Meta:
        model = FriendRequest
        fields = ['from_user', 'to_user', 'created_at']


class FriendshipOutSerializer(serializers.ModelSerializer):
    friend = serializers.CharField(source='friend.username')

    class Meta:
        model = Friendship
        fields = ['friend', 'created_at']

class FriendshipsOutSerializer(serializers.ModelSerializer):
    friends = FriendshipOutSerializer(many=True, source='friendships')

    class Meta:
        model = DefaultUser
        fields = ['friends']

class FriendshipMessagesOutSerializer(serializers.ModelSerializer):
    friend = serializers.CharField(source='friend.username')
    messages = MessageOutSerializer(many=True)

    class Meta:
        model = Friendship
        fields = ['friend', 'created_at', 'messages']

class MessagesOutSerializer(serializers.ModelSerializer):
    friendships = FriendshipMessagesOutSerializer(many=True)
    incoming_friendships = FriendshipMessagesOutSerializer(many=True)

    class Meta:
        model = DefaultUser
        fields = ['friendships', 'incoming_friendships']

class FriendRequestsOutSerializer(serializers.ModelSerializer):
    sent_friend_requests = FriendRequestOutSerializer(many=True)
    received_friend_requests = FriendRequestOutSerializer(many=True)

    class Meta:
        model = DefaultUser
        fields = ['sent_friend_requests', 'received_friend_requests']
