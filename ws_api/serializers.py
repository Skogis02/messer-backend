from rest_framework import serializers
from api.models import FriendRequest, DefaultUser


class ConsumerSpecificSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'consumer' in self.context, AssertionError("Context missing key 'consumer'.")
        self.consumer = self.context['consumer']


class EndpointInSerializer(ConsumerSpecificSerializer):
    endpoint = serializers.ChoiceField(choices=[])
    content = serializers.JSONField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endpoint'].choices = self.consumer.endpoints.keys()

    def validate(self, data):
        endpoint = self.consumer.endpoints[data['endpoint']]
        if not endpoint.serializer:
            return {'endpoint': endpoint, 'content': None}
        endpoint_serializer = endpoint.serializer(data=data['content'], context={'consumer': self.consumer})
        if not endpoint_serializer.is_valid():
            raise serializers.ValidationError(endpoint_serializer.errors)
        return {'endpoint': endpoint, 'content': endpoint_serializer}


class SendMessageSerializer(ConsumerSpecificSerializer):
    friend = serializers.CharField()
    content = serializers.CharField()

    def validate(self, data):
        friendship_queryset = self.consumer.user.friendships.filter(friend__username=data['friend'])
        if not friendship_queryset.exists():
            raise serializers.ValidationError("That user is not in your friend list.", code='Forbidden')
        return {'friendship': friendship_queryset.first(), 'content': data['content']}


class SendFriendRequestSerializer(ConsumerSpecificSerializer):
    to_user = serializers.CharField()

    def validate(self, data):
        to_user = data['to_user']
        to_user_queryset = DefaultUser.objects.filter(username=to_user)
        if not to_user_queryset.exists():
            raise serializers.ValidationError('That user does not exists.', code='Not Found')
        friend_request = FriendRequest(from_user=self.consumer.user, to_user=to_user_queryset.first())
        return {'friend_request': friend_request}


class RespondToFriendRequestSerializer(ConsumerSpecificSerializer):
    from_user = serializers.CharField()
    accept = serializers.BooleanField()

    def validate(self, data):
        from_user, accept = data['from_user'], data['accept']
        friend_request_queryset = self.consumer.user.received_friend_requests.filter(from_user__username=from_user)
        if not friend_request_queryset.exists():
            raise serializers.ValidationError('You do not have any pending friend requests from that user.')
        return {'friend_request': friend_request_queryset.first(), 'accept': accept}


class RemoveFriendSerializer(ConsumerSpecificSerializer):
    friend = serializers.CharField()

    def validate(self, data):
        friend = data['friend']
        friendship_queryset = self.consumer.user.friendships.filter(friend__username=friend)
        if not friendship_queryset.exists():
            raise serializers.ValidationError('You do not have a friend with that name.')
        return {'friendship': friendship_queryset.first()}


class WithdrawFriendRequestSerializer(ConsumerSpecificSerializer):
    to_user = serializers.CharField()

    def validate(self, data):
        to_user = data['to_user']
        friend_request_queryset = self.consumer.user.sent_friend_requests.filter(to_user__username=to_user)
        if not friend_request_queryset.exists():
            raise serializers.ValidationError('You do not have a pending friend request sent to that user.')
        return {'friend_request': friend_request_queryset.first()}