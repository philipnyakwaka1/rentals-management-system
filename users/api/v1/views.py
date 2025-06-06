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
from users.models import Profile, UserBuilding
from buildings.models import Building
from announcements.models import Notice, Comment
from users.pagination import CustomPaginator
from django.urls import reverse, exceptions
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import PermissionDenied, ValidationError



def check_permission_retrieve_user(request, user_id):
    if not IsAdminUser().has_permission(request, None):
        if request.user.pk != user_id:
            raise PermissionDenied('user not authorized to perform this action')

def check_permission_filter_users_by_building(request, building):
    if not IsAdminUser().has_permission(request, None):
        if not UserBuilding.objects.filter(building=building, profile=request.user.profile).exists():
            raise PermissionDenied('user profile not linked to building')

def check_permission_modify_profile(building, request):
    if not IsAdminUser().has_permission(request, None):
        try:
            user_building = UserBuilding.objects.get(profile=request.user.profile, building=building)
            if user_building.relationship != 'owner':
                raise PermissionDenied('user does not have permission to modify this building')
        except UserBuilding.DoesNotExist:
            raise PermissionDenied('user does not have permission to modify this building, profile not linked to building')

@api_view(['PUT'])
def user_register(request):
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
def user_login(request):
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
def user_logout(request):
    response = Response({'message': 'successfully logged out'})
    response.delete_cookie('refresh_token')
    return response

@api_view(['GET'])
@permission_classes([IsAdminUser])
def users_list(request):
    all_users = User.objects.all()
    paginator = CustomPaginator()
    paginated_queryset = paginator.paginate_queryset(all_users, request)
    users = list(map(lambda x : {'user': {**UserSerializer(x).data, 'profile': UserProfileSerializer(x.profile).data}}, paginated_queryset))
    return paginator.get_paginated_response(users)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_retrieve_update(request, user_id):
    try:
        check_permission_retrieve_user(request, user_id)
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
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
def profile_retrieve_update(request, user_id):
    try:
        check_permission_retrieve_user(request, user_id)
        user = User.objects.get(pk=user_id)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

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
def users_list_by_building(request, building_id):
    def paginate_data(data):
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(data, request)
        users = list(map(lambda x: {'user': { **UserSerializer(x.profile.user).data, 'profile': UserProfileSerializer(x.profile).data }}, paginated_queryset))
        return (paginator, users)
    
    try:
        building = Building.objects.get(pk=building_id)
        check_permission_filter_users_by_building(request, building)
        query_param = request.query_params.get('relationship')
        linked_profiles = UserBuilding.objects.filter(building=building)
        if query_param == 'owner' or query_param == 'tenant':
            users = list(filter(lambda x: x.relationship == query_param, linked_profiles))
            results = paginate_data(users)
            return results[0].get_paginated_response(results[1])
        results = paginate_data(linked_profiles)
        return results[0].get_paginated_response(results[1])
    except Building.DoesNotExist:
        return Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_profile_to_building(request, building_id):

    def validate_add_profile(user,building):
        try:
            user_building = UserBuilding.objects.get(profile=user.profile)
            raise ValueError('profile already linked to building')
        except Exception as e:
            pass

    try:
        building = Building.objects.get(pk=building_id)
        check_permission_modify_profile(building, request)
    except Building.DoesNotExist:
        return  Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    if 'user_id' in request.data and 'relationship' in request.data:
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
            validate_add_profile(user, building)
        except User.DoesNotExist:
            return  Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status-status.HTTP_409_CONFLICT)
        
        if hasattr(user, 'profile'):
            user.profile.buildings.add(building, through_defaults={'relationship': request.data.get('relationship')})
            return Response({'message': f'profile with user id {user.pk} successful added to building id {building.pk}'}, status=status.HTTP_200_OK)
        return Response({'error': 'user profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'must provide user id and relationship to building'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_profile_from_building(request, building_id, user_id):
    try:
        building = Building.objects.get(pk=building_id)
        check_permission_modify_profile(building, request)
        user = User.objects.get(pk=user_id)
        owners = UserBuilding.objects.filter(relationship='owner')
        if len(owners) == 1 and owners.first().profile == user.profile:
            raise ValidationError('cannot delete building only owner')
        user_building = UserBuilding.objects.get(profile=user.profile, building=building)
        user_building.delete()
        return Response({'status': 'profile-building link succesfully deleted'}, status=status.HTTP_200_OK)
    except Building.DoesNotExist:
        return  Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserBuilding.DoesNotExist:
        return Response({'error': 'user profile not linked to building'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        return Response({'error': 'cannot delete building only owner'}, status=status.HTTP_400_BAD_REQUEST)