from rest_framework import serializers
from .models import DefaultUser
from django.contrib.auth.hashers import make_password


class DefaultUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, data):
        return make_password(data)


class DefaultLoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)






