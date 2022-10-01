from rest_framework import serializers
from .models import DefaultUser, Message
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

    class Meta:
        model = Message
        fields = ['from_user', 'created_at', 'has_been_read', 'read_at', 'content']








