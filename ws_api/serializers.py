from rest_framework import serializers

USERNAME_MAX_LENGTH = 50
MESSAGE_MAX_LENGTH = 200

class BaseWsSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WsMessageContent(serializers.Field):
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class WsMessageSerializer(BaseWsSerializer):
    id = serializers.IntegerField(min_value=1, max_value=99)
    endpoint = serializers.ChoiceField(choices=[])
    content = WsMessageContent()

    def __init__(self, endpoints: list, data):
        super().__init__(data=data)
        self.fields['endpoint'].choices = endpoints

class SendMessageSerializer(BaseWsSerializer):
    friend = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    content = serializers.CharField(max_length=MESSAGE_MAX_LENGTH)

class SendFriendRequestSerializer(BaseWsSerializer):
    to_user = serializers.CharField(max_length=USERNAME_MAX_LENGTH)

class RespondToFriendRequestSerializer(BaseWsSerializer):
    from_user = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    accept = serializers.BooleanField()

class WithdrawFriendRequestSerializer(BaseWsSerializer):
    to_user = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
