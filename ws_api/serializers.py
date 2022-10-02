from rest_framework import serializers
import json


class EndpointInSerializer(serializers.Serializer):
    endpoint = serializers.ChoiceField(choices=[])
    content = serializers.JSONField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        assert 'consumer' in self.context, AssertionError("Context missing key 'consumer'.")
        self.consumer = self.context['consumer']
        self.fields['endpoint'].choices = self.consumer.endpoints.keys()

    def validate(self, data):
        endpoint = self.consumer.endpoints[data['endpoint']]
        if not endpoint.serializer:
            return {'endpoint': endpoint, 'content': None}
        endpoint_serializer = endpoint.serializer(data=data['content'], context={'consumer': self.consumer})
        if not endpoint_serializer.is_valid():
            print(self.errors)
            raise serializers.ValidationError
        return {'endpoint': endpoint, 'content': endpoint_serializer}


class SendMessageSerializer(serializers.Serializer):
    friend = serializers.CharField()
    content = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        assert 'consumer' in self.context, AssertionError("Context missing key 'consumer'.")
        self.consumer = self.context['consumer']

    def validate(self, data):
        friendship_queryset = self.consumer.user.friendships.filter(friend__username=data['friend'])
        if not friendship_queryset.exists():
            raise serializers.ValidationError
        return data









