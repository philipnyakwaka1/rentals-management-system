from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from users.serializers import UserSerializer, UserProfileSerializer
from buildings.serializers import BuildingsSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.models import Profile
from buildings.models import Building
from announcements.models import Notice, Comment


@api_view(['POST'])
def JWT_login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if not check_password(password, user.password):
        return Response({'error': 'invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
def register_user_api(request):
    try:
        username = request.data.get('username')
        user = User.objects.get(username=username)
        return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
#@permission_classes([IsAdminUser])
def get_users_api(request):
    all_users = User.objects.all()
    users = list(map(lambda x : {'user': {**UserSerializer(x).data, 'profile': UserProfileSerializer(x.profile).data}}, all_users))
    return Response({'users': users})

@api_view(['GET', 'PATCH'])
def get_update_user_api(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{user.username} succesfully updated', 'updates': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        user_profile = UserProfileSerializer(user.profile).data
        user_data = serializer.data
        user_data['profile'] = user_profile
        return Response({'user': user_data}, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
def get_update_profile_api(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'profile': { **serializer.data, 'user': UserSerializer(user).data}}, status=status.HTTP_200_OK)
        return Response({serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        profile_serializer = UserProfileSerializer(profile)
        user_serializer = UserSerializer(user)
        return Response({'user': { **user_serializer.data, 'profile': profile_serializer.data}}, status=status.HTTP_200_OK)

@api_view(['GET'])    
def user_buildings(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    buildings = profile.buildings.all()
    if len(buildings) != 0:
        all_buildings = list(map(lambda x: BuildingsSerializer(x).data, buildings))
    return Response({'user': { **UserSerializer(user).data, "buildings": all_buildings}}, status=status.HTTP_200_OK)
