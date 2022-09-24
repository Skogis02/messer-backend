from rest_framework import serializers
from .models import DefaultUser


class DefaultUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
