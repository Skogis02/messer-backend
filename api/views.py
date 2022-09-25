from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import DefaultUser, Friendship, FriendRequest, Message
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DefaultUserSerializer, DefaultLoginSerializer


class Register(APIView):

    def post(self, request):
        serializer = DefaultUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):

    def post(self, request):
        serializer = DefaultLoginSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({'Authentication failed': 'Insufficient credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        username, password = serializer.data['username'], serializer.data['password']
        user = DefaultUser.objects.filter(username=username).first()
        if not (user and user.check_password(raw_password=password)):
            return Response({'Authentication failed': 'Invalid credentials.'}, status=status.HTTP_404_NOT_FOUND)
        login(request, user)
        return Response({'Authentication succeeded': 'Logged in.'}, status=status.HTTP_200_OK)


class VerifySession(APIView):

    def post(self, request):
        return Response(status=status.HTTP_200_OK)






# Create your views here.

