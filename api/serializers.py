from rest_framework import serializers
from .models import DefaultUser


class DefaultRegistrationSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    password = None

    def validate(self, data):
        username_collisions = DefaultUser.objects.filter(username=data['username'])
        if username_collisions:
            raise serializers.ValidationError('That username is already taken!')
        email_collisions = DefaultUser.objects.filter(username=data['email'])
        if email_collisions:
            raise serializers.ValidationError('That email is already assigned to another account!')
        if not data['password1'] == data['password2']:
            raise serializers.ValidationError('Passwords do not match!')
        validated_data = {'username': data['username'],
                          'email': data['email'],
                          'password': data['password1']
                          }
        return validated_data

    def create(self, validated_data):
        return DefaultUser.objects.create(**validated_data)
