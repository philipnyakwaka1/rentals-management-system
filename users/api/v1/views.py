from django.contrib.auth.models import User
from users.serializers import UserSerializer, UserProfileSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Profile


@api_view(['PUT'])
def register_user_api(request):
    username = request.data.get('username')
    user = User.objects.get(username=username)
    if user:
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def update_user_profile_api(request):
    profile = Profile.objects.get(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)