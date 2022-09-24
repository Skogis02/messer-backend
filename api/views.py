from django.shortcuts import render
from .models import DefaultUser, Friendship, FriendRequest, Message
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DefaultRegistrationSerializer


class Register(APIView):

    def post(self, request):
        serializer = DefaultRegistrationSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Create your views here.

