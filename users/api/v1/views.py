from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.hashers import check_password
from users.serializers import UserSerializer, UserProfileSerializer
from buildings.serializers import BuildingsSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.models import Profile
from buildings.models import Building
from announcements.models import Notice, Comment
from users.pagination import CustomPaginator
from django.urls import reverse, exceptions
from django.db.models.deletion import ProtectedError

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def JWT_login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)
    if not check_password(password, user.password):
        return Response({'error': 'invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    response = Response({
        'access': str(refresh.access_token),
    }, status=status.HTTP_200_OK)

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        secure=False, #only in development
        httponly=True,
        samesite='Strict' #check 'Lax' option
    )
    
    return response

@api_view(['GET'])
def refresh_tokens(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(refresh_token)
        return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({'error': 'invalid or expired token'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def logout(request):
    response = Response({'message': 'successfully logged out'})
    response.delete_cookie('refresh_token')
    return response

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_users_api(request):
    all_users = User.objects.all()
    paginator = CustomPaginator()
    paginated_queryset = paginator.paginate_queryset(all_users, request)
    users = list(map(lambda x : {'user': {**UserSerializer(x).data, 'profile': UserProfileSerializer(x.profile).data}}, paginated_queryset))
    return paginator.get_paginated_response(users)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_update_delete_user_api(request, user_pk):
    if request.user.pk != user_pk and not request.user.is_staff:
        return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        user_id = user.pk
        try:
            user.delete()
            return Response({'message': f'user id {user_id} succesfully deleted'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response('building has an unresolved notice', status=status.HTTP_409_CONFLICT)

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
        return Response(user_data, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_update_delete_profile_api(request, user_pk):
    if request.user.pk != user_pk:
        return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        user_id = profile.user.pk
        profile.delete()
        return Response({'message': f'user id {user_id} profile succesfully deleted'}, status=status.HTTP_200_OK)

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
@permission_classes([IsAuthenticated])    
def user_buildings(request, user_pk):
    if request.user.pk != user_pk:
        return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    buildings = profile.buildings.all()
    paginator = CustomPaginator()
    paginated_queryset = paginator.paginate_queryset(buildings, request)
    all_buildings = list(map(lambda x: BuildingsSerializer(x).data, paginated_queryset))
    return paginator.get_paginated_response(all_buildings)
