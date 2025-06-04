from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from users.models import Profile
from buildings.models import Building
from buildings.serializers import BuildingsSerializer
from announcements.serializers import CommentSerializer, NoticeSerializer
from users.serializers import UserSerializer, UserProfileSerializer
from django.core import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from buildings.pagination import CustomPaginator
from django.db.models.deletion import ProtectedError
from users.models import UserBuilding
from rest_framework.exceptions import PermissionDenied, ValidationError

"""
Attention
===============

unauthenticated_users_can only access building owners, not tenants


"""

def check_permission_create_building(request, user_id):
        if not IsAdminUser().has_permission(request, None):
            if request.user.pk != int(user_id):
                raise PermissionDenied('user does not have permission to perform this action')

def check_permission_modify_profile(building, request):
    if not IsAdminUser().has_permission(request, None):
        try:
            user_building = UserBuilding.objects.get(profile=request.user.profile, building=building)
            if user_building.relationship != 'owner':
                raise PermissionDenied('user does not have permission to modify this building')
        except UserBuilding.DoesNotExist:
            raise PermissionDenied('user does not have permission to modify this building, profile not linked to building')
        
def check_permission_access_linked_data(request, building):
    if not IsAdminUser().has_permission(request, None):
        if not UserBuilding.objects.filter(building=building, profile=request.user.profile).exists():
            raise PermissionDenied('user profile not linked to building')

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_query_buildings(request):

    if request.method =='GET':
        all_buildings = Building.objects.all()
        geojson = request.query_params.get('geojson') == 'true'
        if geojson:
            buildings = serializers.serialize('geojson', all_buildings)
            return Response(buildings)
        
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_buildings, request)
        buildings = list(map(lambda x: serializers.serialize('geojson', [x]), paginated_queryset))
        return paginator.get_paginated_response(buildings)

    if request.method == 'PUT':
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
            profile = Profile.objects.get(user=user)
            check_permission_create_building(request, request.data.get('user_id'))
            serializer = BuildingsSerializer(data=request.data)
            if serializer.is_valid():
                building = serializer.save()
                profile.buildings.add(building, through_defaults={'relationship': 'owner'})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({'error': 'user profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_building_profile(request, building_id):

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
def delete_building_profile(request, building_id, user_id):
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

@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_update_building_api(request, building_id):

    def check_permission(building, user):
        try:
            if not IsAdminUser().has_permission(request, None):
                user_building = UserBuilding.objects.get(profile=user.profile, building=building)
                if user_building.relationship != 'owner':
                    raise PermissionDenied('user does not have permission to modify this building')
        except UserBuilding.DoesNotExist:
            raise PermissionDenied('user profile is not linked to the building')

    try:
        building = Building.objects.get(pk=building_id)
    except Building.DoesNotExist:
        return Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = serializers.serialize('geojson', [building])
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        try:
            check_permission(building, request.user)
            building.delete()
            return Response({'building_id': building_id, 'status': 'succesfully deleted'})
        except ProtectedError as e:
            return Response({'error': 'building has an unresolved notice'}, status=status.HTTP_409_CONFLICT)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        try:
            check_permission(building, request.user)
            serializer = BuildingsSerializer(building, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Buiding succesfully updated', 'building': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def building_users(request, building_id):
    def paginate_data(data):
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(data, request)
        users = list(map(lambda x: {'user': { **UserSerializer(x.profile.user).data, 'profile': UserProfileSerializer(x.profile).data }}, paginated_queryset))
        return (paginator, users)
    
    try:
        building = Building.objects.get(pk=building_id)
        check_permission_access_linked_data(request, building)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])    
def user_buildings(request, user_pk):

    def paginate_buildings(data):
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(data, request)
        all_buildings = list(map(lambda x: Building(x.building).data, paginated_queryset))
        return (paginator, all_buildings)

    try:
        check_permission_access_linked_data(request, user_pk)
        user = User.objects.get(pk=user_pk)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    category = request.query_params.get('category')
    if category not in ['owner', 'tenant']:
        return Response(
            {'error': "Missing or invalid 'category' query parameter. Expected 'owned' or 'rented'."},
            status=status.HTTP_400_BAD_REQUEST)
    
    buildings = UserBuilding.objects.filter(profile=profile, relationship=category)
    response = paginate_buildings(buildings)
    return response[0].get_paginated_response(response[1])
        