from django.shortcuts import render
from django.contrib.auth import login
from .models import DefaultUser, Friendship, FriendRequest, Message
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DefaultUserSerializer


class Register(APIView):

    def post(self, request):
        serializer = DefaultUserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):

    def post(self, request):
        if not (request.data['username'] and request.data['password']):
            return Response({'Authentication failed': 'Insufficient credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            username = request.data['username']
            password = request.data['password']
            print(username, password)
            user = DefaultUser.objects.filter(username=username).first()
            if not (user and user.check_password(raw_password=password)):
                return Response({'Authentication failed': 'Invalid credentials.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                login(request, user)
                return Response({'Authentication succeeded': 'Logged in.'}, status=status.HTTP_200_OK)






# Create your views here.

